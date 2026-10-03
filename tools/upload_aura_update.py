#!/usr/bin/env python3
"""Install a matching application through private pairing and pinned device HTTPS."""
import argparse,json,os,time
from pathlib import Path
import esptool,serial
from backup_device import EXPECTED_MAC,require_expected_mac
from test_aura_network import read_uart,uart_status,screen_png,private_pairing_ocr,PinnedLocal,ota_restart,require

def main():
    def progress(stage):
        print(json.dumps({'stage':stage}),flush=True)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True);p.add_argument('--application',type=Path,required=True);p.add_argument('--version',required=True);p.add_argument('--summary',type=Path,required=True);a=p.parse_args()
    require_expected_mac()
    if a.summary.exists():p.error('summary already exists')
    progress('verify_identity_and_reset')
    esp=esptool.connect_esp(port=a.port,chip='esp32s3',initial_baud=115200,before='default-reset',connect_attempts=1)
    try:
        require(':'.join(f'{b:02x}' for b in esp.read_mac())==EXPECTED_MAC,'Device identity differs')
        esp._port.dtr=False;esp._port.rts=False;esp.hard_reset();esp._port.dtr=False;esp._port.rts=False
    finally:esp._port.close()
    port=serial.Serial(port=None,baudrate=115200,timeout=.2,exclusive=True);port.dtr=False;port.rts=False;port.port=a.port;port.open()
    try:
        boot=read_uart(port,9,maximum=131072)
        require(not any(x in boot for x in (b'Guru Meditation',b'Backtrace:',b'AURA_FATAL',b'Brownout')),'Initial boot failed')
        deadline=time.monotonic()+240
        while time.monotonic()<deadline:
            status=uart_status(port)
            if status and status.get('wifi')==1 and status.get('time')==1:break
            time.sleep(2)
        else:raise RuntimeError('Router or clock did not become ready')
        progress('pair_before_update')
        address,code=private_pairing_ocr(screen_png(port));client=PinnedLocal(address)
        http,paired=client.json('/api/pair',method='POST',data={'code':code},unauthenticated=True);code=''
        require(http==200 and paired.get('paired') is True,'Device pairing failed');client.csrf=paired['csrf']
        http,before=client.json('/api/status')
        preserved_fields=('city','latitude','longitude','brightness','alwaysOnDisplay','ssid','widgetConfig')
        require(http==200 and all(key in before for key in preserved_fields),'Pre-update settings are unavailable')
        progress('upload_and_verify_restart')
        ota_restart(client,port,a.application,180)
        # UART status contains firmware version without authentication material.
        port.write(b'status\n');raw=read_uart(port,3,maximum=16384)
        require(('version='+a.version).encode() in raw,'Updated application reports a different version')
        deadline=time.monotonic()+180
        while time.monotonic()<deadline:
            status=uart_status(port)
            if status and status.get('wifi')==1 and status.get('time')==1:break
            time.sleep(2)
        else:raise RuntimeError('Updated router or clock did not become ready')
        progress('pair_after_update')
        address,code=private_pairing_ocr(screen_png(port));updated=PinnedLocal(address)
        updated.pin=client.pin
        http,paired=updated.json('/api/pair',method='POST',data={'code':code},unauthenticated=True);code=address=''
        require(http==200 and paired.get('paired') is True,'Post-update pairing failed');updated.csrf=paired['csrf']
        http,after=updated.json('/api/status')
        require(http==200 and after.get('firmware')=='AURA Desk '+a.version,'Post-update firmware status differs')
        require(all(key in after and before[key]==after[key] for key in preserved_fields),'Saved settings changed during update')
        progress('saved_settings_verified')
        summary={'passed':True,'version':a.version,'https_application_update':True,'healthy_restart':True,
                 'settings_preserved':True,'saved_configs_and_display_compared':True,'tls_certificate_preserved':True,
                 'selected_brightness':after['brightness'],'always_on':after['alwaysOnDisplay']}
        fd=os.open(a.summary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as out:json.dump(summary,out,indent=2);out.write('\n')
        print(json.dumps(summary),flush=True)
    finally:
        port.write(b'screen:0\n');port.flush();port.close()

if __name__=='__main__':main()
