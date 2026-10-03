#!/usr/bin/env python3
"""Read back OTA selection and application hashes; never writes external flash."""
import argparse,binascii,hashlib,json,os,struct
from pathlib import Path
import esptool
from backup_device import connect,EXPECTED_MAC

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True);p.add_argument('--application',type=Path,required=True);p.add_argument('--summary',type=Path,required=True);a=p.parse_args()
    if a.summary.exists():p.error('summary already exists')
    application=a.application.read_bytes();expected=hashlib.md5(application).hexdigest()
    esp,security=connect(a.port,115200)
    try:
        data=esptool.read_flash(esp,0xf000,8192,flash_size='16MB',no_progress=True)
        copies=[]
        for index,offset in enumerate((0,4096)):
            sequence=struct.unpack_from('<I',data,offset)[0];state,crc=struct.unpack_from('<II',data,offset+24)
            valid=sequence!=0xffffffff and state==2 and crc==(binascii.crc32(data[offset:offset+4],0xffffffff)&0xffffffff)
            copies.append({'copy':index,'sequence':sequence,'state':state,'valid':valid})
        valid=[item for item in copies if item['valid']]
        if not valid:raise RuntimeError('No CRC-valid accepted OTA application')
        selected=max(valid,key=lambda item:item['sequence'])
        if selected['sequence']!=2:raise RuntimeError('Expected the first verified browser update in sequence 2')
        if esp.flash_md5sum(0x520000,len(application))!=expected:raise RuntimeError('Updated OTA application differs from release')
        if esp.flash_md5sum(0x20000,len(application))!=expected:raise RuntimeError('Previous valid application differs from release')
        summary={'passed':True,'active_partition':'ota_1','active_offset':'0x520000','active_state':'VALID','ota_sequence':2,'metadata':copies,'application_bytes':len(application),'application_sha256':hashlib.sha256(application).hexdigest(),'both_application_md5_readbacks_match_release':True,'flash_writes':False,'efuse_writes':False}
        fd=os.open(a.summary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as out:json.dump(summary,out,indent=2);out.write('\n')
        print(json.dumps(summary),flush=True)
        esp._port.dtr=False;esp._port.rts=False;esp.hard_reset();esp._port.dtr=False;esp._port.rts=False
    finally:esp._port.close()

if __name__=='__main__':main()
