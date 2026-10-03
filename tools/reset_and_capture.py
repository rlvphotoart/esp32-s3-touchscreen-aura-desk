#!/usr/bin/env python3
"""Identity-checked normal reboot with a private bounded serial boot capture."""
import argparse,json,os,re,time
from pathlib import Path
import esptool
from backup_device import EXPECTED_MAC

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--seconds',type=float,default=15)
    a=p.parse_args()
    if not 0<a.seconds<=60:p.error('seconds must be within (0,60]')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(a.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:
        # Enter ROM briefly to verify identity, then boot the preserved app.
        esp=esptool.connect_esp(port=a.port,chip='esp32s3',initial_baud=115200,before='default-reset',connect_attempts=1)
        try:
            if ':'.join(f'{b:02x}' for b in esp.read_mac())!=EXPECTED_MAC:
                raise RuntimeError('device identity mismatch')
            # A no-reset connection can retain asserted default modem lines.
            # Release BOOT/EN before the normal reset pulse and the capture.
            esp._port.dtr=False
            esp._port.rts=False
            esp.hard_reset()
            esp._port.dtr=False
            esp._port.rts=False
            esp._port.timeout=0.2
            end=time.monotonic()+a.seconds
            while time.monotonic()<end:
                data=esp._port.read(max(1,min(esp._port.in_waiting,4096)))
                if data:f.write(data)
        finally:esp._port.close()
    s=a.output.read_bytes().decode('utf8','replace')
    summary={'port':a.port,'seconds':a.seconds,'bytes':a.output.stat().st_size,
             'rom_boot_count':s.count('ESP-ROM:esp32s3-20210327'),
             'board_profile_seen':'Jingcai:ESP32_4848S040C_I_Y_3' in s,
             'board_initialize_success':'Board initialize success' in s,
             'board_begin_success':'Board begin success' in s,
             'psram_initialized_yes':'psram_initialized=yes' in s,
             'psram_8mib_reported':'psram_bytes=8388608' in s,
             'auth_expire_count':s.count('AUTH_EXPIRE'),
             'crash_markers':{k:s.count(k) for k in ['Guru Meditation','Backtrace:','PANIC','Brownout']},
             'rom_reset_lines':re.findall(r'^rst:[^\r\n]+',s,re.M)}
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
