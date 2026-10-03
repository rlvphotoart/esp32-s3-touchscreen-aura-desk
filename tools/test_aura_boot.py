#!/usr/bin/env python3
"""Bounded hardware boot/endurance checks; records only non-secret result summaries."""
import argparse,json,os,re,time
from pathlib import Path
import esptool
from backup_device import EXPECTED_MAC,require_expected_mac
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True)
    p.add_argument('--count',type=int,default=10);p.add_argument('--directory',type=Path,required=True);a=p.parse_args()
    require_expected_mac()
    if not 1<=a.count<=10:p.error('count must be 1..10')
    a.directory.mkdir(parents=True,exist_ok=False);a.directory.chmod(0o700);results=[]
    for number in range(1,a.count+1):
        esp=esptool.connect_esp(port=a.port,chip='esp32s3',initial_baud=115200,before='default-reset',connect_attempts=1)
        data=bytearray()
        try:
            if ':'.join(f'{b:02x}' for b in esp.read_mac())!=EXPECTED_MAC:raise RuntimeError('device identity mismatch')
            esp._port.dtr=False;esp._port.rts=False;esp.hard_reset();esp._port.dtr=False;esp._port.rts=False;esp._port.timeout=.2
            end=time.monotonic()+12
            while time.monotonic()<end:data.extend(esp._port.read(max(1,min(esp._port.in_waiting,4096))))
        finally:esp._port.close()
        fd=os.open(a.directory/f'boot-{number:02}.bin',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as f:f.write(data)
        text=data.decode('utf8','replace')
        result={'boot':number,'ready':'AURA_READY' in text,'healthy':'AURA_HEALTH startup=passed' in text,
                'rom_boots':text.count('ESP-ROM:esp32s3-20210327'),
                'crash_markers':{key:text.count(key) for key in ('Guru Meditation','Backtrace:','PANIC','Brownout','AURA_FATAL')},
                'status':re.findall(r'AURA_STATUS[^\r\n]+',text)}
        results.append(result);print(json.dumps(result),flush=True)
        (a.directory/'results.json').write_text(json.dumps(results,indent=2)+'\n');(a.directory/'results.json').chmod(0o600)
        if not result['ready'] or not result['healthy'] or result['rom_boots']!=1 or any(result['crash_markers'].values()):raise RuntimeError('boot validation failed; inspect private evidence')
    print(f'PASS: {a.count} consecutive boots with display/UI/startup health and no crash markers.',flush=True)
if __name__=='__main__':main()
