#!/usr/bin/env python3
"""Read only allowlisted non-key eFuse fields through Espressif's public API."""
import argparse, os
from pathlib import Path
import espefuse

FIELDS = '''WR_DIS RD_DIS DIS_DOWNLOAD_ICACHE DIS_DOWNLOAD_DCACHE DIS_FORCE_DOWNLOAD SOFT_DIS_JTAG DIS_PAD_JTAG DIS_DOWNLOAD_MANUAL_ENCRYPT SPI_BOOT_CRYPT_CNT SECURE_BOOT_EN SECURE_BOOT_AGGRESSIVE_REVOKE SECURE_BOOT_KEY_REVOKE0 SECURE_BOOT_KEY_REVOKE1 SECURE_BOOT_KEY_REVOKE2 KEY_PURPOSE_0 KEY_PURPOSE_1 KEY_PURPOSE_2 KEY_PURPOSE_3 KEY_PURPOSE_4 KEY_PURPOSE_5 DIS_USB_JTAG DIS_USB_SERIAL_JTAG STRAP_JTAG_SEL DIS_DOWNLOAD_MODE DIS_USB_SERIAL_JTAG_DOWNLOAD_MODE ENABLE_SECURITY_DOWNLOAD DIS_USB_OTG_DOWNLOAD_MODE SECURE_VERSION FLASH_TYPE FLASH_CAP FLASH_VENDOR PSRAM_CAP PSRAM_VENDOR PKG_VERSION WAFER_VERSION_MAJOR WAFER_VERSION_MINOR_LO WAFER_VERSION_MINOR_HI VDD_SPI_FORCE VDD_SPI_TIEH SPI_PAD_CONFIG_CLK SPI_PAD_CONFIG_Q SPI_PAD_CONFIG_D SPI_PAD_CONFIG_CS SPI_PAD_CONFIG_HD SPI_PAD_CONFIG_WP SPI_PAD_CONFIG_DQS SPI_PAD_CONFIG_D4 SPI_PAD_CONFIG_D5 SPI_PAD_CONFIG_D6 SPI_PAD_CONFIG_D7'''.split()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--before', choices=['no-reset','default-reset'], default='no-reset')
    a = p.parse_args()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    previous_mask = os.umask(0o077)
    try:
        f = a.output.open('x', encoding='utf-8')
    finally:
        os.umask(previous_mask)
    with f:
        esp = espefuse.get_esp(port=a.port, baud=115200, before=a.before, chip='esp32s3')
        try:
            mac = ':'.join(f'{b:02x}' for b in esp.read_mac())
            if mac != os.environ.get('AURA_EXPECTED_MAC',''):
                raise RuntimeError('Device MAC identity mismatch')
            commands = espefuse.init_commands(esp=esp)
            known = {e.name for e in commands.efuses}
            missing = set(FIELDS) - known
            if missing:
                raise RuntimeError('Unsupported eFuse field names: ' + ', '.join(sorted(missing)))
            commands.summary(efuses_to_show=FIELDS, format='json', file=f)
        finally:
            esp._port.close()

if __name__ == '__main__':
    main()
