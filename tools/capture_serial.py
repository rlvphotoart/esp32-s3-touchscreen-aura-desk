#!/usr/bin/env python3
"""Bounded receive-only capture; never transmit application commands or reset lines."""
import argparse, json, os, re, time
from pathlib import Path
import serial

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--port', required=True)
p.add_argument('--baud', type=int, default=115200)
p.add_argument('--seconds', type=float, default=15)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
if not 0 < a.seconds <= 300:
    p.error('seconds must be within (0, 300]')
a.output.parent.mkdir(parents=True, exist_ok=True)
s = serial.Serial(port=None, baudrate=a.baud, timeout=0.2, rtscts=False, dsrdtr=False, exclusive=True)
s.dtr = False
s.rts = False
s.port = a.port
fd = os.open(a.output, os.O_CREAT | os.O_WRONLY | os.O_EXCL, 0o600)
with os.fdopen(fd, 'wb') as f:
    try:
        s.open()
        end = time.monotonic() + a.seconds
        while time.monotonic() < end:
            data = s.read(max(1, min(s.in_waiting, 4096)))
            if data:
                f.write(data)
    finally:
        s.close()
data = a.output.read_bytes()
text = data.decode('utf-8', 'replace')
# Print only recognized ROM boot fields; raw application logs stay private locally.
boot = [line for line in text.splitlines() if re.match(r'^(ets |rst:|boot:|configsip:|clk_drv:|mode:|load:|entry |ESP-ROM:|Build:)', line)]
print(json.dumps({'port': a.port, 'baud': a.baud, 'seconds': a.seconds, 'bytes': len(data), 'output': str(a.output.resolve()), 'rom_boot_lines': boot[:40]}, indent=2))
