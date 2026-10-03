#!/usr/bin/env python3
"""Export known original flash regions and hash manifest offline; never decode secrets."""
import hashlib,json,subprocess,sys
from pathlib import Path
from backup_device import private_write

ROOT=Path(__file__).resolve().parents[1]

def main():
    root=ROOT/'backups'
    subprocess.run([sys.executable,str(ROOT/'tools/verify_backup.py'),str(root)],check=True)
    image=(root/'full_flash_original.bin').read_bytes()
    manifest=json.loads((root/'manifest.json').read_text())
    regions={'bootloader_region.bin':(0,0x8000),'partition_table.bin':(0x8000,0x1000),
             'nvs.bin':(0x9000,0x6000),'factory_partition.bin':(0x10000,0x700000),
             'coredump.bin':(0x710000,0x10000)}
    for name,(off,size) in regions.items():
        data=image[off:off+size]
        path=root/name
        if path.exists():
            if path.read_bytes()!=data:raise RuntimeError(f'Existing artifact differs from full image: {name}')
            path.chmod(0o600)
        else:private_write(path,data)
    app=(ROOT/'logs/original_factory_image.bin').read_bytes()
    if image[0x10000:0x10000+len(app)]!=app:raise RuntimeError('Validated application differs from full image')
    if not (root/'application_image.bin').exists():private_write(root/'application_image.bin',app)
    for name,source in {'chip_info.txt':'chip_info.txt','flash_info.txt':'flash_info.txt',
                        'security_info.txt':'security_info.txt','efuse_summary_filtered.json':'efuse_summary_filtered.json'}.items():
        if not (root/name).exists():private_write(root/name,(ROOT/'logs'/source).read_bytes())
    manifest['region_exports']={name:{'offset':hex(off),'bytes':size} for name,(off,size) in regions.items()}
    manifest['region_exports']['application_image.bin']={'offset':'0x10000','bytes':len(app)}
    manifest['commands_used']=[
        '.venv/bin/python tools/device_inventory.py',
        'ioreg -r -n "USB Serial" -l -w 0',
        '.venv/bin/python tools/capture_serial.py --port /dev/cu.usbserial-10 --baud 115200 --seconds 15 --output logs/passive_115200.bin',
        '.venv/bin/python -m esptool --port /dev/cu.usbserial-10 --baud 115200 --connect-attempts 2 --before default-reset --after no-reset --no-stub chip-id',
        '.venv/bin/python -m esptool --chip esp32s3 --port /dev/cu.usbserial-10 --baud 115200 --before no-reset --after no-reset --no-stub get-security-info',
        '.venv/bin/python -m esptool --chip esp32s3 --port /dev/cu.usbserial-10 --baud 115200 --before no-reset --after no-reset --no-stub flash-id',
        '.venv/bin/python tools/read_efuses.py --port /dev/cu.usbserial-10 --output logs/efuse_summary_filtered.json (at acquisition: no key-block output)',
        '.venv/bin/python -m esptool --chip esp32s3 --port /dev/cu.usbserial-10 --baud 230400 --before default-reset --after no-reset --no-stub read-flash --flash-size 16MB --no-progress 0x0 0x10000 backups/original_boot_region.bin',
        '.venv/bin/python -u tools/backup_device.py --port /dev/cu.usbserial-10 --output-directory backups --baud 230400 (earlier reader revision: incomplete at2MiB)',
        '.venv/bin/python -u tools/backup_device.py --port /dev/cu.usbserial-10 --output-directory backups --baud 230400 --resume (recovered at115200; stopped deliberately to enable verified erased-region acquisition)',
        '.venv/bin/python -u tools/backup_device.py --port /dev/cu.usbserial-10 --output-directory backups --baud 115200 --resume --verify-erased',
        '.venv/bin/python tools/vendor/gen_esp32part.py --flash-size 16MB --offset 0x8000 --primary-bootloader-offset 0x0 backups/partition_table.bin backups/partition_table_decoded.txt',
        '.venv/bin/python -m esptool --chip esp32s3 image-info backups/bootloader_region.bin',
        '.venv/bin/python -m esptool --chip esp32s3 image-info logs/original_factory_image.bin',
        './scripts/verify_backup.sh',
        './scripts/restore_original.sh (review-only)']
    manifest['failures_and_recovery']=[
        {'stage':'460800 baud full read','result':'serial timeout; no complete backup produced','log':'logs/backup_read.txt'},
        {'stage':'230400 baud1MiB reads','result':'corruptSLIPdata atthirdchunk; valid2MiB prefix retained','log':'logs/backup_chunked.txt'},
        {'stage':'230400 baud64KiB resumed reads','result':'packeterror; switched115200; latercontrolled stop to enable verified-erased optimization','log':'logs/backup_resumed.txt'},
        {'stage':'115200 resumed verified acquisition','result':'complete16MiB; full-device MD5 matches','log':'logs/backup_verified_erased.txt'}]
    manifest['files']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                       for p in root.iterdir() if p.is_file() and p.name not in ('manifest.json','.gitkeep','SHA256SUMS')}
    temp=root/'manifest.complete.json'
    private_write(temp,(json.dumps(manifest,indent=2)+'\n').encode())
    temp.replace(root/'manifest.json')
    sums=''.join(f"{v['sha256']}  {name}\n" for name,v in sorted(manifest['files'].items()))
    private_write(root/'SHA256SUMS',sums.encode())
    (root/'partition_table_decoded.txt').chmod(0o600)
    print('Exported original regions; all exports match the verified complete flash snapshot.')

if __name__=='__main__':main()
