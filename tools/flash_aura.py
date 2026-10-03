#!/usr/bin/env python3
"""Install the validated AURA release after proving the current full-flash backup."""
import argparse, binascii, hashlib, json, os, struct, subprocess, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import esptool
from backup_device import EXPECTED_MAC, EXPECTED_JEDEC, FLASH_BYTES,require_expected_mac

ROOT=Path(__file__).resolve().parents[1]

def app_only_image(snapshot, regions):
    """Validate the initial ota0 installation and prepare a byte-preserving update."""
    if len(snapshot)!=FLASH_BYTES:
        raise RuntimeError('app-only backup is not a full 16 MiB snapshot')
    for offset,data in regions[:2]:
        if snapshot[offset:offset+len(data)]!=data:
            raise RuntimeError('app-only requires the existing bootloader and partition table to match this release')
    table=regions[1][1]
    partitions={}
    for start in range(0,len(table),32):
        entry=table[start:start+32]
        if len(entry)!=32: raise RuntimeError('truncated partition table')
        magic=struct.unpack_from('<H',entry)[0]
        if magic in (0xffff,0xebeb): break
        if magic!=0x50aa: raise RuntimeError('invalid partition table magic')
        _,kind,subtype,offset,size,label,_=struct.unpack('<HBBII16sI',entry)
        name=label.split(b'\0',1)[0].decode('ascii')
        if name in partitions: raise RuntimeError('duplicate partition label')
        partitions[name]=(kind,subtype,offset,size)
    required={'otadata':(1,0,0xf000,0x2000),'ota_0':(0,0x10,0x20000,0x500000),
              'ota_1':(0,0x11,0x520000,0x500000)}
    if any(partitions.get(name)!=entry for name,entry in required.items()):
        raise RuntimeError('app-only requires the known AURA dual-slot partition layout')
    metadata=snapshot[0xf000:0x11000]
    ota_state={'active_partition':'ota_0','copies':[]}
    for copy in range(2):
        sector=metadata[copy*4096:(copy+1)*4096]
        if sector==b'\xff'*4096:
            ota_state['copies'].append({'copy':copy,'erased':True})
            continue
        sequence,=struct.unpack_from('<I',sector,0)
        state,crc=struct.unpack_from('<II',sector,24)
        # Matches ESP-IDF 5.3.2 bootloader_common_ota_select_crc and otatool.py.
        expected_crc=binascii.crc32(sector[:4],0xffffffff)&0xffffffff
        if sequence!=1 or state!=2 or crc!=expected_crc or sector[32:]!=b'\xff'*(4096-32):
            raise RuntimeError('app-only requires erased OTA metadata or CRC-valid sequence 1 in VALID state; another slot/update state needs OTA or explicit recovery')
        ota_state['copies'].append({'copy':copy,'sequence':sequence,'state':'VALID','crc_valid':True})
    offset,application=regions[2]
    if offset!=0x20000 or not application or len(application)>0x500000:
        raise RuntimeError('app-only application does not fit ota_0')
    end=offset+len(application)
    sector_end=(end+4095)&~4095
    expected=bytearray(snapshot)
    expected[offset:end]=application
    # esptool erases whole 4 KiB sectors. Restore the verified tail of the final
    # sector so every byte outside the new application remains unchanged.
    write_data=application+snapshot[end:sector_end]
    return bytes(expected),[(offset,write_data)],ota_state

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',required=True)
    p.add_argument('--backup',type=Path,required=True)
    p.add_argument('--release',type=Path,default=ROOT/'releases/aura-desk-1.0.0')
    p.add_argument('--execute',action='store_true')
    p.add_argument('--erase-all',action='store_true')
    p.add_argument('--app-only',action='store_true',help='update the known initial ota0 installation while preserving settings and cache; requires --execute')
    a=p.parse_args()
    require_expected_mac()
    if a.app_only and not a.execute: p.error('--app-only requires --execute')
    if a.app_only and a.erase_all: p.error('--app-only cannot be combined with --erase-all')
    backup=a.backup.resolve(); release=a.release.resolve()
    subprocess.run([sys.executable,str(ROOT/'tools/verify_backup.py'),str(backup)],check=True)
    saved=json.loads((backup/'manifest.json').read_text())
    if saved['mac']!=EXPECTED_MAC or saved['chip']!='ESP32-S3': raise RuntimeError('backup identity mismatch')
    layout=json.loads((release/'build-layout.json').read_text())
    if layout['chip']!='esp32s3' or layout['flash_size_bytes']!=FLASH_BYTES or layout['application_offset']!='0x20000':
        raise RuntimeError('release target/layout mismatch')
    regions=[]
    for entry in layout['regions']:
        path=(release/entry['file']).resolve()
        if path.parent!=release: raise RuntimeError('release path escape')
        data=path.read_bytes()
        if len(data)!=entry['bytes'] or hashlib.sha256(data).hexdigest()!=entry['sha256']: raise RuntimeError('release artifact changed')
        regions.append((int(entry['offset'],16),data))
    merged=(release/layout['merged_image']['file']).read_bytes()
    if len(merged)!=FLASH_BYTES or hashlib.sha256(merged).hexdigest()!=layout['merged_image']['sha256']: raise RuntimeError('merged image changed')
    if [offset for offset,_ in regions]!=[0,0x8000,0x20000]: raise RuntimeError('unexpected write offsets')
    plan={'mode':'execute' if a.execute else 'review','port':a.port,'mac':EXPECTED_MAC,
          'backup':str(backup),'erase_all':a.erase_all,'regions':layout['regions'],'efuse_changes':False}
    expected=merged; writes=regions
    if a.app_only:
        snapshot=(backup/'full_flash_original.bin').read_bytes()
        if len(snapshot)!=FLASH_BYTES or hashlib.md5(snapshot).hexdigest()!=saved['full_flash_original.bin']['md5']:
            raise RuntimeError('app-only backup changed after local verification')
        expected,writes,ota_state=app_only_image(snapshot,regions)
        plan.update(mode='app-only',execute=True,regions=[layout['regions'][2]],
                    write_bytes=len(writes[0][1]),preserved_final_sector_bytes=len(writes[0][1])-len(regions[2][1]),
                    ota_state=ota_state,expected_flash_sha256=hashlib.sha256(expected).hexdigest())
    print(json.dumps(plan,indent=2),flush=True)
    if not a.execute: return
    if not a.app_only and not a.erase_all: p.error('initial install requires explicit --erase-all')
    esp=esptool.connect_esp(port=a.port,chip='esp32s3',initial_baud=115200,before='default-reset',connect_attempts=1)
    try:
        if ':'.join(f'{b:02x}' for b in esp.read_mac())!=EXPECTED_MAC: raise RuntimeError('device MAC mismatch')
        security=esp.get_security_info()
        if security['flags']!=0 or security['flash_crypt_cnt']!=0: raise RuntimeError('unexpected security state')
        esptool.attach_flash(esp)
        if esp.flash_id(cache=False)!=EXPECTED_JEDEC: raise RuntimeError('flash identity mismatch')
        esp=esptool.run_stub(esp); esptool.attach_flash(esp)
        if esp.flash_md5sum(0,FLASH_BYTES)!=saved['full_flash_original.bin']['md5']:
            raise RuntimeError('current flash differs from backup: take a fresh backup before installing')
        if a.app_only:
            print('Live full-device hash matches preserved backup. Updating only ota0; settings, cache and OTA metadata are preserved.',flush=True)
        else:
            print('Live full-device hash matches preserved backup. Erasing all external flash as authorized.',flush=True)
            esptool.erase_flash(esp)
        esptool.write_flash(esp,writes,flash_freq='keep',flash_mode='keep',flash_size='keep',compress=True)
        whole_md5=esp.flash_md5sum(0,FLASH_BYTES)
        if whole_md5!=hashlib.md5(expected).hexdigest(): raise RuntimeError('full installed flash differs from expected image; keep device in ROM and repair')
        record={**plan,'completed_at':datetime.now(ZoneInfo('Europe/Bucharest')).isoformat(),
                'whole_device_md5':whole_md5,'merged_sha256':hashlib.sha256(merged).hexdigest(),
                'device_flash_verified':True,'secure_boot':False,'flash_encryption':False,'esptool_version':esptool.__version__}
        destination=ROOT/'logs'/('aura-install-'+datetime.now(ZoneInfo('Europe/Bucharest')).strftime('%Y%m%d-%H%M%S')+'.json')
        fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f: json.dump(record,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
        print('PASS: all 16 MiB match the validated '+('application overlay with preserved settings and cache' if a.app_only else 'release')+'. Booting AURA Desk.',flush=True)
        esp._port.dtr=False; esp._port.rts=False; esp.hard_reset(); esp._port.dtr=False; esp._port.rts=False
    finally: esp._port.close()
if __name__=='__main__': main()
