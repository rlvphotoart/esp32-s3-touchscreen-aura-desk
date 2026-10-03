#!/usr/bin/env python3
"""AURA UART command/screenshot client. Never toggles BOOT/EN or prints credentials."""
import argparse,os,time
from pathlib import Path
import serial
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--port',required=True)
    p.add_argument('--command',default='status'); p.add_argument('--output',type=Path); p.add_argument('--seconds',type=float,default=5)
    p.add_argument('--screen',type=int,choices=range(14),help='show this page before the command in the same serial session')
    a=p.parse_args()
    if not 0<a.seconds<=60: p.error('seconds must be within 0..60')
    if a.command=='screenshot' and not a.output: p.error('screenshot requires --output')
    port=serial.Serial(port=None,baudrate=115200,timeout=.2,exclusive=True)
    port.dtr=False;port.rts=False;port.port=a.port;port.open()
    try:
        # Some WCH drivers pulse EN when opening even with both lines released.
        # Wait through a possible boot before sending, so Serial.begin cannot
        # discard the command. Keep captured boot diagnostics private.
        boot=bytearray(); settle=time.monotonic()+9
        while time.monotonic()<settle:
            block=port.read(max(1,min(port.in_waiting,4096)))
            if block: boot.extend(block)
        if a.screen is not None:
            port.write(f'screen:{a.screen}\n'.encode()); time.sleep(1)
        port.write((a.command+'\n').encode()); data=bytearray(); deadline=time.monotonic()+a.seconds
        while time.monotonic()<deadline:
            block=port.read(max(1,min(port.in_waiting,16384)))
            if block:data.extend(block)
            if a.command=='screenshot' and b'\nAURA_SCREEN_END\n' in data: break
        if a.output:
            a.output.parent.mkdir(parents=True,exist_ok=True)
            fd=os.open(a.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'wb') as f:f.write(data)
            print(f'Saved {len(data):,} bytes to {a.output}')
        else:
            # Only our own non-secret engineering protocol is displayed.
            for line in data.decode('utf8','replace').splitlines():
                if line.startswith(('AURA_STATUS','AURA_HEALTH','AURA_ERROR')): print(line)
    finally:port.close()
if __name__=='__main__':main()
