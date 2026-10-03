#!/usr/bin/env python3
"""Read-only, identity-checked, resumable ESP32-S3 backup using Espressif APIs."""
import argparse, hashlib, json, os, re, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import esptool
import serial

EXPECTED_MAC = os.environ.get('AURA_EXPECTED_MAC', '').lower()
FLASH_BYTES = 0x1000000
EXPECTED_JEDEC = 0x184068
CHUNK_BYTES = 0x10000

def require_expected_mac():
    """Fail before touching hardware unless the operator supplied its identity."""
    if not EXPECTED_MAC:
        raise RuntimeError('Set AURA_EXPECTED_MAC to your verified device MAC before hardware maintenance')
    if re.fullmatch(r'(?:[0-9a-f]{2}:){5}[0-9a-f]{2}', EXPECTED_MAC) is None:
        raise RuntimeError('AURA_EXPECTED_MAC must contain six colon-separated hexadecimal octets')
    return EXPECTED_MAC

def private_write(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())

def finish_commit(out):
    """Recover/publish an already verified image locally; never open hardware."""
    partial, target = out/'full_flash_original.bin.partial', out/'full_flash_original.bin'
    pending, final = out/'manifest.json.pending', out/'manifest.json'
    if any(path.is_symlink() for path in (partial,target,pending,final)):
        raise RuntimeError('commit artifacts cannot be symlinks')
    manifest=json.loads(pending.read_text())
    expected=manifest['full_flash_original.bin']
    if not expected.get('device_md5_verified') or expected['bytes']!=FLASH_BYTES:
        raise RuntimeError('pending manifest lacks full-device verification')
    source=partial if partial.exists() else target
    data=source.read_bytes()
    if len(data)!=FLASH_BYTES or hashlib.sha256(data).hexdigest()!=expected['sha256'] or hashlib.md5(data).hexdigest()!=expected['md5']:
        raise RuntimeError('pending image does not match its verified commit record')
    if target.exists():
        if target.read_bytes()!=data:
            raise RuntimeError('existing final image differs; refusing commit')
    else:
        os.link(source,target)
    if final.exists():
        if json.loads(final.read_text())!=manifest:
            raise RuntimeError('existing manifest differs; refusing commit')
    else:
        os.link(pending,final)
    # Cleanup only after both final artifacts are present and verified.
    pending.unlink()
    if partial.exists():
        partial.unlink()

def connect(port, baud):
    require_expected_mac()
    esp = esptool.connect_esp(port=port, chip='esp32s3', initial_baud=115200, before='default-reset', connect_attempts=1)
    try:
        mac = ':'.join(f'{b:02x}' for b in esp.read_mac())
        if esp.CHIP_NAME != 'ESP32-S3' or mac != EXPECTED_MAC:
            raise RuntimeError(f'device identity mismatch: {esp.CHIP_NAME}, {mac}')
        security = esp.get_security_info()
        if security['flags'] != 0 or security['flash_crypt_cnt'] != 0:
            raise RuntimeError('unexpected security state; stopped before running RAM stub')
        esptool.attach_flash(esp)
        flash_id = esp.flash_id(cache=False)
        if flash_id != EXPECTED_JEDEC:
            raise RuntimeError(f'flash identity mismatch: {flash_id:#x}')
        # Official volatile RAM reader. No flash write/erase or eFuse writes are called.
        stub = esptool.run_stub(esp)
        esp = stub
        if baud != 115200:
            esp.change_baud(baud)
        esptool.attach_flash(esp)
        return esp, security
    except BaseException:
        esp._port.close()
        raise

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port')
    p.add_argument('--output-directory', type=Path, required=True)
    p.add_argument('--baud', type=int, choices=[115200,230400], default=230400)
    p.add_argument('--resume', action='store_true', help='resume only a locally saved prefix that matches the same device')
    p.add_argument('--verify-erased', action='store_true', help='save erased 64 KiB regions only after device MD5 equals the known all-FF digest')
    p.add_argument('--reference-image', type=Path, help='reuse reference blocks only when their MD5 matches a fresh device-side MD5')
    p.add_argument('--recover-commit', action='store_true', help='finish an interrupted verified-image/manifest publication offline')
    a = p.parse_args()
    out = a.output_directory.resolve()
    if a.recover_commit:
        finish_commit(out)
        print(f'Recovered verified backup commit offline: {out}')
        return
    if not a.port:
        p.error('--port is required for acquisition')
    require_expected_mac()
    out.mkdir(parents=True, exist_ok=True)
    out.chmod(0o700)
    target, partial = out/'full_flash_original.bin', out/'full_flash_original.bin.partial'
    for name in (target, out/'manifest.json'):
        if name.exists() or name.is_symlink():
            p.error(f'refusing to overwrite backup artifact: {name}')
    if (out/'manifest.json.pending').exists() or (out/'manifest.json.pending').is_symlink():
        p.error('pending commit exists; inspect and use --recover-commit')
    if partial.is_symlink():
        p.error('partial backup cannot be a symlink')
    if partial.exists() != a.resume:
        p.error('existing partial requires --resume; --resume requires an existing partial')
    if not a.resume and (out/'application_probe.bin').exists():
        p.error('existing application probe: choose a fresh directory')
    prefix = partial.read_bytes() if a.resume else b''
    reference = a.reference_image.read_bytes() if a.reference_image else None
    if reference is not None and len(reference) != FLASH_BYTES:
        p.error('reference image must be exactly 16 MiB')
    if len(prefix) > FLASH_BYTES or len(prefix) % CHUNK_BYTES:
        p.error('partial length is not aligned/in bounds')
    started = datetime.now(ZoneInfo('Europe/Bucharest')).isoformat()
    esp, security = connect(a.port, a.baud)
    retries = 0
    current_baud = a.baud
    try:
        if prefix:
            if esp.flash_md5sum(0,len(prefix)) != hashlib.md5(prefix).hexdigest():
                raise RuntimeError('saved prefix differs from the device; refusing resume')
            print(f'Validated {len(prefix):,} saved bytes against device MD5; resuming.',flush=True)
        if not a.resume:
            app = esptool.read_flash(esp,0x10000,CHUNK_BYTES,flash_size='16MB',no_progress=True)
            private_write(out/'application_probe.bin',app)
        sha, md5 = hashlib.sha256(prefix), hashlib.md5(prefix)
        chunks = [{'offset':hex(off),'length':CHUNK_BYTES,'method':'saved-prefix-device-md5-verified','sha256':hashlib.sha256(prefix[off:off+CHUNK_BYTES]).hexdigest()}
                  for off in range(0,len(prefix),CHUNK_BYTES)]
        erased = b'\xff' * CHUNK_BYTES
        erased_md5 = hashlib.md5(erased).hexdigest()
        transfer = time.monotonic()
        flags = os.O_WRONLY | (os.O_APPEND if a.resume else os.O_CREAT | os.O_EXCL)
        flags |= getattr(os,'O_NOFOLLOW',0)
        fd=os.open(partial,flags,0o600)
        with os.fdopen(fd,'ab' if a.resume else 'wb') as f:
            if os.fstat(f.fileno()).st_size != len(prefix):
                raise RuntimeError('partial file changed during preparation')
            os.fchmod(f.fileno(),0o600)
            for offset in range(len(prefix),FLASH_BYTES,CHUNK_BYTES):
                for attempt in range(3):
                    try:
                        reference_block = reference[offset:offset+CHUNK_BYTES] if reference is not None else None
                        device_block_md5 = esp.flash_md5sum(offset,CHUNK_BYTES) if reference is not None or a.verify_erased else None
                        if reference_block is not None and device_block_md5 == hashlib.md5(reference_block).hexdigest():
                            data=reference_block
                            method='reference-block-fresh-device-md5-verified'
                        elif a.verify_erased and device_block_md5 == erased_md5:
                            data=erased
                            method='device-md5-confirmed-erased-fill'
                        else:
                            data=esptool.read_flash(esp,offset,CHUNK_BYTES,flash_size='16MB',no_progress=True)
                            method='direct-read-with-device-md5'
                        break
                    except (esptool.FatalError,serial.SerialException) as e:
                        retries += 1
                        print(f'Read error at {offset:#x}: {e}. Retry {retries}; no partial chunk saved.',flush=True)
                        esp._port.close()
                        if attempt==2 or retries>=5:
                            raise
                        current_baud=115200  # conservative fallback after any stream corruption
                        esp,security=connect(a.port,current_baud)
                if len(data)!=CHUNK_BYTES:
                    raise RuntimeError('short read')
                # esptool validates each read against the stub-provided MD5 before returning.
                f.write(data);f.flush();os.fsync(f.fileno())
                sha.update(data);md5.update(data)
                chunks.append({'offset':hex(offset),'length':len(data),'method':method,'sha256':hashlib.sha256(data).hexdigest()})
                if (offset+CHUNK_BYTES)%0x100000==0:
                    print(f'Backup progress: {(offset+CHUNK_BYTES)/FLASH_BYTES:.0%}; elapsed {time.monotonic()-transfer:.0f}s',flush=True)
        remote_md5=esp.flash_md5sum(0,FLASH_BYTES)
        if remote_md5!=md5.hexdigest():
            raise RuntimeError('full-image device MD5 does not match backup')
        manifest={'started_at':started,'completed_at':datetime.now(ZoneInfo('Europe/Bucharest')).isoformat(),
                  'serial_port':a.port,'chip':esp.CHIP_NAME,'mac':EXPECTED_MAC,'jedec_id':hex(EXPECTED_JEDEC),
                  'flash_size_bytes':FLASH_BYTES,'offset':0,'initial_baud':a.baud,'final_baud':current_baud,
                  'resumed_prefix_bytes':len(prefix),'retry_count':retries,'esptool_version':esptool.__version__,
                  'verify_erased_enabled':a.verify_erased,'acquisition':'direct reads plus optional freshly device-MD5-confirmed reference/erased blocks; full-device MD5 verifies the final image',
                  'reference_sha256':hashlib.sha256(reference).hexdigest() if reference is not None else None,
                  'python_api':'esptool.connect_esp / attach_flash / run_stub / read_flash / flash_md5sum',
                  'security_flags':security['flags'],'flash_crypt_count':security['flash_crypt_cnt'],
                  'full_flash_original.bin':{'bytes':partial.stat().st_size,'sha256':sha.hexdigest(),'device_md5_verified':True,'md5':remote_md5},
                  'chunks':chunks,'flash_writes_issued':False,'efuse_writes_issued':False,
                  'note':'May contain private configuration. Keep local and out of Git. ROM and eFuses are outside external flash.'}
        private_write(out/'manifest.json.pending',(json.dumps(manifest,indent=2)+'\n').encode())
        finish_commit(out)
        print(f'Backup complete: {target}; SHA256 {sha.hexdigest()}; device MD5 matches.',flush=True)
    finally:
        esp._port.close()

if __name__=='__main__':main()
