#!/usr/bin/env python3
"""Capture checked Home/Weather/Tools framebuffers without pairing or credentials."""
import argparse,hashlib,os,re,subprocess,sys,time
from pathlib import Path
import serial
from test_aura_network import read_uart,uart_status,require

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True);a=p.parse_args()
    port=serial.Serial(port=None,baudrate=115200,timeout=.2,exclusive=True)
    port.dtr=False;port.rts=False;port.port=a.port;port.open()
    try:
        boot=read_uart(port,9,maximum=131072)
        require(not any(marker in boot for marker in (b'Guru Meditation',b'Backtrace:',b'AURA_FATAL',b'Brownout')), 'Initial capture boot reported a failure')
        deadline=time.monotonic()+180
        while time.monotonic()<deadline:
            status=uart_status(port)
            if status and all(status.get(k)==1 for k in ('wifi','time','internet','weather','air','rates','board')):break
            time.sleep(2)
        else:raise RuntimeError('Live data was not ready for the release capture')
        print('Live router, time and provider data ready.',flush=True)
        for page,name in ((0,'home'),(1,'weather'),(2,'tools')):
            port.write(f'screen:{page}\n'.encode());read_uart(port,1,maximum=16384)
            port.reset_input_buffer();port.write(b'screenshot\n')
            raw=read_uart(port,60,marker=b'\nAURA_SCREEN_END\n',maximum=480*480*2+16384)
            header=re.search(rb'AURA_SCREEN (\d+) (\d+) (\d+) ([0-9a-f]{64})\r?\n',raw)
            require(header is not None,'No checked screenshot header')
            width,height,length=map(int,header.groups()[:3]);pixels=raw[header.end():header.end()+length]
            require(width==height==480 and length==460800 and len(pixels)==length,'Invalid release capture dimensions')
            require(raw[header.end()+length:].startswith(b'\nAURA_SCREEN_END'),'Interrupted screenshot framing')
            require(hashlib.sha256(pixels).hexdigest().encode()==header[4],'Screenshot hash differs from device')
            path=ROOT/'logs'/f'aura-release-{name}.bin'
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'wb') as out:out.write(raw)
            destination=ROOT/'artifacts'/f'device-{name}.png'
            subprocess.run([sys.executable,str(ROOT/'tools/screen_to_png.py'),str(path),str(destination)],check=True)
        print('PASS: three exact device framebuffers captured; all pixel SHA-256 values match.',flush=True)
    finally:
        port.write(b'screen:0\n');port.flush();port.close()

if __name__=='__main__':main()
