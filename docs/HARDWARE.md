# Connected device — hardware evidence

Investigated on 3 October 2026, Europe/Bucharest. The owner requested identification and understanding before firmware development. No firmware/flash/eFuse writes or GPIO probing were issued. Official Espressif ROM queries and a volatile official RAM reading stub were used; entering download mode required purposeful hardware resets. Raw evidence and backups remain local and ignored by Git.

## Confirmed device and connection

| Field | Measured / reported value | Evidence |
| --- | --- | --- |
| Chip family | ESP32-S3 | ROM chip identification; image target ID 9 |
| Package / silicon revision | QFN56 / v0.2 | esptool and read-only eFuses |
| Main CPU capability | Dual Xtensa LX7, up to 240 MHz | Chip features and datasheet; running CPU frequency not measured |
| Base MAC | `<runtime-device-mac>` | ROM read; host tools bind this board identity |
| Crystal | 40 MHz | esptool |
| Flash | 16 MiB (16,777,216 bytes), JEDEC `68 40 18` | Flash ID/capacity query |
| Flash bus / voltage | Four data lines / 3.3 V | eFuses `FLASH_TYPE`, `VDD_SPI_FORCE/TIEH` |
| Existing image flash settings | DIO, 80 MHz, 16 MB | Both original bootloader/application headers; no mode change written |
| Embedded PSRAM | 8 MiB, vendor code `AP_3v3` | Chip features and PSRAM eFuses |
| Existing runtime PSRAM report | Initialized; 8,388,608 bytes | Original firmware diagnostics; no memory stress test |
| USB device | Product `USB Serial`, VID/PID `1A86:7523`, bcdDevice `0264` | USB registry |
| USB descriptors | Manufacturer and serial-number descriptors absent | Registry `iManufacturer=0`, `iSerialNumber=0` |
| Host USB driver | AppleUSBCHCOM | USB → interface → driver → serial registry ancestry |
| Serial path | `/dev/cu.usbserial-10` (`/dev/tty.usbserial-10` counterpart) | Registry ancestry, pySerial USB descriptors and successful ROM response |
| USB physical location / link | `0x00100000`, 12 Mbit/s USB link | Registry; USB speed is separate from UART baud |
| Original serial baud | 115200 | Decodable ROM/application boot output |
| External GPIO attachments | None, per owner | Owner's reply; onboard circuitry still exists |

The empty output from `system_profiler SPUSBDataType` did not hide the device: IORegistry and pySerial supplied the descriptor and serial-path evidence. No additional USB serial driver was needed.

## Board identity and confidence

**Confirmed firmware-selected profile:** `Jingcai:ESP32_4848S040C_I_Y_3`. It appears in original startup initialization/begin messages and compiled application DROM. Startup reports successful board initialization and reads touch product ID bytes `39 31 31` (ASCII `911`) and configuration version 250.

**Strongly inferred physical board:** Jingcai/Guition **ESP32-4848S040C_I_Y_3**, a 4-inch 480×480 RGB display platform using ST7701 and GT911. The exact firmware-selected profile matches Espressif's documented board, drivers and memory configuration. This is strong combined evidence, while physical PCB silkscreen, module shield ordering code and board revision have not been independently inspected. The working visible image and touch coordinates remain untested. [Official matching board profile](https://github.com/esp-arduino-libs/ESP32_Display_Panel/blob/master/docs/board/board_jingcai.md)

**Likely bridge family:** WCH CH340 or compatible UART interface. VID/PID and Apple CHCOM identify a compatible interface; they do not prove its exact package/subtype. [WCH USB/UART product family](https://www.wch.cn/products/CH340.html)

**Likely flash vendor:** Boya, matching the official ESP-IDF `0x68` manufacturer probe. Exact flash part/suffix remains unknown. **Likely silicon ordering variant:** ESP32-S3R8, consistent with 8 MiB embedded 3.3 V PSRAM. Neither inference determines a module marketing name. [Official Boya probe](https://github.com/espressif/esp-idf/blob/v6.1/components/spi_flash/spi_flash_chip_boya.c), [ESP32-S3 variant table](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf)

## Important board-level consequences

The official reference profile consumes GPIO19 for touch SDA and GPIO20 for LCD data. Native USB D−/D+ use those same pins, so native USB is not a suitable additional feature while retaining this reference display/touch wiring. The observed USB-UART bridge is the proven console/download path.

GPIO26–37 are reserved for memory; the profile also uses boot straps for display/touch after reset. Use the separate [GPIO map](GPIO_MAP.md) before future initialization. A generic ESP32 DevKit pinout is inappropriate. The configured profile is an evidence-backed reference, not a continuity test or proof that the installed library has no overrides.

## Remaining measurements

Exact PCB/module/revision markings; electrical pin routing and expansion-header mapping; flash component suffix; regulator and antenna implementation; actual CPU frequency/free heap; PSRAM stress reliability; visible LCD and touch interaction; Wi-Fi/BLE end-to-end connectivity; board power consumption. These remain unset instead of being inferred from available silicon features.

The machine-readable profile is `docs/hardware_profile.json`. Local evidence includes `logs/usb_registry.txt`, `serial_inventory.json`, `chip_info.txt`, `flash_info.txt`, `security_info.txt`, `efuse_summary_filtered.json` and private serial captures. Keys were excluded from eFuse output.
