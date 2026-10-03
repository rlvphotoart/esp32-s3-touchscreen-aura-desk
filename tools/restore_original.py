#!/usr/bin/env python3
"""Review or explicitly restore the preserved original image on its matching device."""
import argparse,hashlib,json,subprocess,sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import esptool
from backup_device import EXPECTED_MAC,EXPECTED_JEDEC,FLASH_BYTES

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',type=Path,default=ROOT/'backups')
    p.add_argument('--port',required=True)
    p.add_argument('--execute',action='store_true',help='perform the destructive restore after a fresh current-state backup')
    p.add_argument('--confirm-mac',help='required exact device MAC when --execute is selected')
    a=p.parse_args()
    if a.execute and a.confirm_mac!=EXPECTED_MAC:
        p.error('--execute requires --confirm-mac '+EXPECTED_MAC)
    directory=a.directory.resolve()
    subprocess.run([sys.executable,str(ROOT/'tools/verify_backup.py'),str(directory)],check=True)
    manifest=json.loads((directory/'manifest.json').read_text())
    if manifest['chip']!='ESP32-S3' or manifest['mac']!=EXPECTED_MAC or int(manifest['jedec_id'],16)!=EXPECTED_JEDEC:
        p.error('backup device identity mismatch')
    image=(directory/'full_flash_original.bin').read_bytes()
    if len(image)!=FLASH_BYTES or hashlib.sha256(image).hexdigest()!=manifest['full_flash_original.bin']['sha256']:
        p.error('backup image changed or is invalid')
    print(json.dumps({'mode':'execute' if a.execute else 'review-only; no serial port opened',
                      'port':a.port,'chip':'esp32s3','required_mac':EXPECTED_MAC,
                      'image':str(directory/'full_flash_original.bin'),'restore_offset':'0x0','restore_bytes':len(image),
                      'effect':'Restores all external flash, including bootloader, partition table, application, NVS and coredump.',
                      'flash_parameters':'keep original image mode/frequency/size','efuse_changes':False},indent=2),flush=True)
    if not a.execute:
        return
    # Preserve the current device state before any destructive write.
    stamp=datetime.now(ZoneInfo('Europe/Bucharest')).strftime('%Y%m%d-%H%M%S-%f')
    pre=ROOT/'backups'/('pre-restore-'+stamp)
    subprocess.run([sys.executable,str(ROOT/'tools/backup_device.py'),'--port',a.port,
                    '--output-directory',str(pre),'--baud','115200','--verify-erased'],check=True)
    subprocess.run([sys.executable,str(ROOT/'tools/verify_backup.py'),str(pre)],check=True)
    # Revalidate fresh ROM state immediately before writing; no bypass/force options.
    esp=esptool.connect_esp(port=a.port,chip='esp32s3',initial_baud=115200,before='default-reset',connect_attempts=1)
    try:
        if ':'.join(f'{b:02x}' for b in esp.read_mac())!=EXPECTED_MAC:
            raise RuntimeError('device MAC mismatch')
        security=esp.get_security_info()
        if security['flags']!=0 or security['flash_crypt_cnt']!=0:
            raise RuntimeError('security state prevents this restoration procedure')
        esptool.attach_flash(esp)
        if esp.flash_id(cache=False)!=EXPECTED_JEDEC:
            raise RuntimeError('flash identity mismatch')
        esp=esptool.run_stub(esp)
        esptool.attach_flash(esp)
        esptool.write_flash(esp,[(0,image)],flash_freq='keep',flash_mode='keep',flash_size='keep',compress=True)
        if esp.flash_md5sum(0,len(image))!=hashlib.md5(image).hexdigest():
            raise RuntimeError('restored flash does not match original; keep both backups and recover through ROM')
        print('Restored flash verified against original image. Resetting to original firmware.',flush=True)
        esp._port.dtr=False
        esp._port.rts=False
        esp.hard_reset()
    finally:
        esp._port.close()

if __name__=='__main__':main()
