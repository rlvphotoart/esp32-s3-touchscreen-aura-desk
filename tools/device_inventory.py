#!/usr/bin/env python3
"""List serial descriptors without opening ports; select only a unique matching bridge."""
import argparse,json
from serial.tools import list_ports
VID, PID = 0x1A86, 0x7523

def matching_ports():
    return [p for p in list_ports.comports() if p.vid == VID and p.pid == PID]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port-only',action='store_true')
    a=p.parse_args()
    ports=list(list_ports.comports())
    matches=[s for s in ports if s.vid==VID and s.pid==PID]
    if a.port_only:
        if len(matches)!=1:
            p.error(f'expected exactly one {VID:04x}:{PID:04x} UART bridge; found {len(matches)}. Select/verify hardware manually.')
        print(matches[0].device)
        return
    print(json.dumps({'expected_bridge':f'{VID:04x}:{PID:04x}',
                      'candidate_count':len(matches),'candidate_port':matches[0].device if len(matches)==1 else None,
                      'notice':'USB descriptors identify the bridge, not the chip or board. Verify ROM chip and MAC before any write.',
                      'ports':[{'device':s.device,'description':s.description,'vid':f'{s.vid:04x}' if s.vid is not None else None,
                                'pid':f'{s.pid:04x}' if s.pid is not None else None,'location':s.location,'manufacturer':s.manufacturer,
                                'product':s.product,'usb_serial_number':s.serial_number} for s in ports]},indent=2))

if __name__=='__main__':main()
