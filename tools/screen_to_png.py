#!/usr/bin/env python3
"""Decode the device's actual LVGL RGB565 snapshot to a lossless PNG."""
import argparse,hashlib,re,struct,zlib
from pathlib import Path
def chunk(kind,payload):
    return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    raw=a.input.read_bytes();match=re.search(rb'AURA_SCREEN (\d+) (\d+) (\d+)(?: ([0-9a-f]{64}))?\r?\n',raw)
    if not match:raise SystemExit('No device screenshot frame')
    width,height,length=map(int,match.groups()[:3]);data=raw[match.end():match.end()+length]
    if length!=width*height*2 or len(data)!=length or width>1024 or height>1024:raise SystemExit('Invalid/truncated RGB565 snapshot')
    if not raw[match.end()+length:].startswith(b'\nAURA_SCREEN_END'):
        raise SystemExit('Screenshot transfer contains extra bytes or has no terminator; recapture with quiet firmware')
    if match[4] and hashlib.sha256(data).hexdigest().encode()!=match[4]:
        raise SystemExit('Screenshot SHA-256 differs from device; image not accepted')
    rows=bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            i=2*(y*width+x);pixel=data[i]|data[i+1]<<8
            rows.extend((((pixel>>11)&31)*255//31,((pixel>>5)&63)*255//63,(pixel&31)*255//31))
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b'')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(png)
    print(f'Actual device framebuffer: {width}x{height}, {length:,} bytes → {a.output}')
if __name__=='__main__':main()
