# ESP32-S3 research record

Research date: 2026-10-03, Europe/Bucharest. Scope: identify and understand the connected device. These are findings and future design recommendations; no custom firmware, pin initialization, or SDK installation is implied.

## Evidence classes

- **CONFIRMED — observed:** official esptool 5.4.0 identifies ESP32-S3, QFN56, silicon revision v0.2, 40 MHz crystal, dual main cores with a 240 MHz capability, and embedded 8 MB PSRAM (`AP_3v3`). See `logs/chip_info.txt`. The CPU capability is not a measurement of the installed application's runtime frequency. PSRAM identification is not a runtime memory test.
- **CONFIRMED — reported by owner:** nothing is connected externally to the GPIO headers. This does not establish which components exist on the PCB itself.
- **CONFIRMED — investigation evidence:** JEDEC identification reports manufacturer `0x68`, device `0x4018`, capacity 16 MiB; read-only eFuse inspection reports four flash data lines, 3.3 V memory voltage, `DIS_PAD_JTAG=false` and `DIS_USB_JTAG=false`. These establish configuration and enabled debug capability, not physical debug-connector routing. The observed ROM boot message reports DIO and clock divider 1; runtime flash clock must not be inferred from that line alone.
- **CONFIRMED — original firmware report:** its boot sequence declares `Jingcai:ESP32_4848S040C_I_Y_3`, logs successful board initialization, starts ST7701 and GT911 drivers, and reads touch-controller product bytes spelling `911`. `lvgl_v8_port` also appears. This is direct runtime evidence of the firmware's selected board profile and a responding GT911-compatible controller, not a newly installed test program.
- **CONFIRMED — chip documentation:** the resources below document ESP32-S3 silicon. A peripheral being supported by silicon does not establish board routing, attached hardware, enabled firmware, or successful operation.
- **LIKELY — strong board inference:** the runtime board name, display/touch drivers, responding touch product ID, 16 MiB flash and 8 MB PSRAM strongly match the Jingcai/Guition ESP32-4848S040C_I_Y_3 display board. The official library lists this exact profile as 480 × 480, ST7701 with 3-wire SPI + RGB and GT911 over I2C. Firmware selection is confirmed; physical PCB revision and module ordering code remain unverified.
- **LIKELY — chip variant:** the embedded-memory identification matches ESP32-S3R8 silicon in the current datasheet.
- **UNKNOWN:** physical board/module markings and revision, onboard LED/button mappings outside the declared profile, regulator/antenna implementation, exposed expansion-header pinout, runtime PSRAM reliability, and visually correct display/touch behavior. Observed flash and firmware information belongs in `HARDWARE.md` and `FLASH_LAYOUT.md`.

## Current primary documents

| Source | Version or role | What was checked |
|---|---|---|
| [ESP32-S3 datasheet](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf) | v2.2, 2026-03-05 | Variant comparison, pins, straps, memory and peripheral overview |
| [ESP32-S3 Technical Reference Manual](https://documentation.espressif.com/esp32-s3_technical_reference_manual_en.pdf) | Register-level reference | Indexed USB Serial/JTAG PHY-routing section; full PDF exceeded the web reader's size limit |
| [ESP32-S3 hardware design guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html) | Hardware implementation guidance | In-package octal PSRAM pin ownership and USB/power considerations |
| [ESP32-S3 revision v0.2 errata](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32s3/_tags/v0-2.html) | Current errata index | Eight listed issues and individual workaround pages |
| [ESP-IDF v6.1 release](https://github.com/espressif/esp-idf/releases/tag/v6.1) | Stable release, 2026-08-27 | Official release status and installation route |
| [ESP-IDF chip compatibility](https://github.com/espressif/esp-idf/blob/v6.1/COMPATIBILITY.md#esp32-s3) | Release-pinned support matrix | ESP32-S3 v0.1/v0.2 supported since v4.4 |
| [ESP32-S3 SoC capability definitions](https://github.com/espressif/esp-idf/blob/v6.1/components/soc/esp32s3/include/soc/soc_caps.h) | v6.1 source | GPIO, peripheral, memory, power and security capabilities |
| [Official Jingcai board list](https://github.com/esp-arduino-libs/ESP32_Display_Panel/blob/master/docs/board/board_jingcai.md) | Espressif display library | Exact named profile, display and touch controller |
| [Official board profile configuration](https://github.com/esp-arduino-libs/ESP32_Display_Panel/blob/92b790ed6d24b0678e2f45b1fc85f0abd2d41b33/src/board/supported/jingcai/BOARD_JINGCAI_ESP32_4848S040C_I_Y_3.h) | Pinned source commit `92b790e` | RGB/control SPI, touch I2C, backlight pin assignments |

## Declared display-board profile

The runtime evidence materially narrows board identification. The official profile's configuration is documented separately in `GPIO_MAP.md`; it is a reference mapping, not an electrical continuity test or proof of the exact installed library version. Driver version strings do not uniquely establish the display-library source revision.

The reference profile occupies GPIO19 with touch SDA and GPIO20 with LCD data. Native USB on those same chip pins is therefore not a suitable additive feature for this wiring. The profile also uses the boot straps as normal I/O after boot: GPIO0/3/46 for RGB data and GPIO45 for touch SCL. Read-only eFuse evidence shows `VDD_SPI_FORCE=true` and the 3.3 V selection, so GPIO45 does not currently select memory voltage at reset. Preserve that observed configuration; it does not justify modifying eFuses. [Pinned official profile](https://github.com/esp-arduino-libs/ESP32_Display_Panel/blob/92b790ed6d24b0678e2f45b1fc85f0abd2d41b33/src/board/supported/jingcai/BOARD_JINGCAI_ESP32_4848S040C_I_Y_3.h), [chip strap override behavior](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf)

## Framework recommendation for later development

Use **ESP-IDF with C/C++**, target `esp32s3`, for a future modular firmware platform. This is an engineering recommendation based on the desired diagnostics, FreeRTOS services, display/touch GUI, OTA and recovery workflows. The official display-library profile provides a concrete future board configuration to validate against this device before replacement. ESP-IDF does not require inventing a PlatformIO or Arduino board identifier to select this chip target. Existing firmware uses Arduino/LVGL, so a future rewrite should explicitly preserve the working panel/touch sequence rather than adopting an unrelated generic DevKit pinout.

On the research date, Espressif's stable documentation and GitHub release agree on **v6.1**. Pin the exact release and dependencies in a future build; reassess bugfix releases when implementation starts. The chosen display-library/component versions still need a compatibility build with that SDK; this investigation has not demonstrated a custom GUI build. Espressif recommends the Installation Manager (EIM) for obtaining this version. No installation was required for this investigation. [Release source](https://github.com/espressif/esp-idf/releases/tag/v6.1)

## Memory configuration

The observed 8 MB, 3.3 V embedded PSRAM matches octal PSRAM in the chip comparison table. Reserve its bus pins; do not treat this extra RAM as extra flash or usable heap already verified on this board. [Datasheet, table 1-1](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf)

Manufacturer ID `0x68` is consistent with the IDF Boya flash driver. Treat **Boya as likely**, and the exact flash part as unknown until an unambiguous model identifier is obtained. No specific flash-component datasheet is selected solely from capacity. [Espressif's Boya flash driver](https://github.com/espressif/esp-idf/blob/v6.1/components/spi_flash/spi_flash_chip_boya.c)

Flash and PSRAM share MSPI/SPI0/1 and a clock relationship. **Octal PSRAM does not prove octal flash.** Choose flash line mode, capacity and clock from the actual flash evidence. Octal PSRAM uses DDR; quad flash uses SDR. A conservative future configuration can consider 80 MHz only when the actual flash and board support it. Preserve the existing working clock/mode until that is established. The IDF guide marks 120 MHz DDR experimental and describes temperature-sensitive timing failures and calibration requirements. Do not adopt it as a default. [Flash/PSRAM configuration guide](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-guides/flash_psram_config.html)

PSRAM is cached external memory, despite being in-package. When cache is unavailable, access restrictions apply. DMA requirements differ by peripheral, and a future driver must select compatible buffers rather than assuming every allocation can move into PSRAM. Keep critical runtime state and required internal-memory buffers in internal RAM. [External RAM guide](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-guides/external-ram.html)

## USB, JTAG and boot behavior

The observed USB-UART bridge path should be treated separately from native ESP32-S3 USB. A USB serial port belonging to a bridge does not establish that the connector reaches the chip's USB pins.

Native USB uses **GPIO19 = D−**, **GPIO20 = D+**. The fixed-function USB Serial/JTAG controller provides serial console, flashing and debug, while USB OTG supports programmable device/host functions. The controllers share one internal PHY; simultaneous use requires the appropriate external PHY arrangement. The TRM's routing diagram corroborates this distinction. [USB Serial/JTAG guide](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-guides/usb-serial-jtag-console.html), [TRM USB PHY diagram](https://documentation.espressif.com/esp32-s3_technical_reference_manual_en.pdf), [USB device stack](https://docs.espressif.com/projects/esp-idf/en/v6.0/esp32s3/api-reference/peripherals/usb_device.html)

For the firmware-declared Jingcai board, the reference mapping already uses both native USB pins for display/touch. The current USB-UART bridge is the appropriate known console/recovery path. Native USB remains a silicon capability with a board-level conflict, not a promised available connector feature.

The filtered eFuse report has `DIS_USB_OTG_DOWNLOAD_MODE=false`, `DIS_USB_SERIAL_JTAG=false` and `DIS_USB_SERIAL_JTAG_DOWNLOAD_MODE=false`. Those mechanisms are not fuse-disabled on this device. They still have not been tested over a native USB connector, and the declared display profile occupies the relevant pads.

USB host work additionally needs suitable connector wiring and a controlled 5 V VBUS supply. Its silicon support does not prove the PCB can supply a USB peripheral. Native USB firmware should retain a known UART recovery path. Sleep also affects USB Serial/JTAG: Deep-sleep disconnects it; Light-sleep can leave it unresponsive and require reconnection. [USB Serial/JTAG sleep limitations](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-guides/usb-serial-jtag-console.html)

The chip loads a second-stage bootloader from flash; that bootloader selects the application using its configured partition table and OTA state. The ROM download mechanism is a separate recovery path. Do not assume the conventional partition-table offset is the installed offset. [Bootloader guide](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-guides/bootloader.html), [Partition-table guide](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-guides/partition-tables.html)

## Silicon revision v0.2 errata

Revision v0.2 remains covered by the following errata. These are conditional hardware issues, not observed failures of this device.

| Issue | Practical implication for future code | Official source |
|---|---|---|
| ANALOG-160 | Avoid the damaging `BIAS_SLEEP=0`, `PD_CUR=1` sleep combination. Official software workarounds exist in IDF v4.4.2+ and v5.0+; retain them when using touch or ULP sleep. | [Analog power](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32s3/03-errata-description/esp32s3/analog-power-config-might-damage-chip.html) |
| CACHE-126 | Cache write-back can conflict with interrupt or other-core access. Use current IDF cache APIs and their workaround rather than private register sequences. | [Cache write-back](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32s3/03-errata-description/esp32s3/cache-hit-error-during-writeback.html) |
| LCD-239 | Certain RGB/I8080 clock-divider settings can corrupt output. Official LCD drivers in current IDF contain workarounds. | [LCD clocks](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32s3/03-errata-description/esp32s3/lcd-equ-sysclk-issue.html) |
| USBOTG-4289 | Some batches disable ROM USB-OTG download. This device reports its disable bit clear; native USB operation remains untested and conflicts with the reference display/touch wiring. | [USB-OTG download](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32s3/03-errata-description/esp32s3/usb-otg-download-func-bug.html) |
| RMT-176 | Continuous-TX completion may leave an incorrect idle level. Retain the official driver workaround. | [RMT idle level](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32s3/03-errata-description/shared/rmt-idle-level-cannot-be-controlled.html) |
| RTC-126 | RTC register reads after Light-sleep can fail under the affected power-down setting. Current IDF bypasses the condition. | [RTC Light-sleep](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32s3/03-errata-description/shared/rtc-reg-read-error-from-light-sleep.html) |
| ADC-183 | ADC2 digital/DMA acquisition is unsuitable. Prefer ADC1 for continuous sampling; ADC2 requires its supported RTC control path. | [ADC2 DMA](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32s3/03-errata-description/shared/sar-adc-adc2-not-work.html) |
| TOUCH-100 | Raw data from the first two scan-done interrupts is undefined. Follow the documented touch-driver behavior. | [Touch raw data](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32s3/03-errata-description/shared/tchsen-scan-done-int-raw-data-undefined.html) |

## Power-management boundaries

ESP-IDF provides Modem-sleep, automatic Light-sleep and Deep-sleep workflows. Deep-sleep powers down the main CPUs and most RAM and returns through the boot path; retained RTC memory and the ULP enable selected low-power tasks. Wake choices include timers, eligible RTC GPIOs, touch and ULP, with UART/GPIO options for Light-sleep. Maintaining Wi-Fi/BLE connections requires the corresponding driver-managed sleep workflow. Whole-board current also includes the regulator, USB bridge and LEDs, so datasheet chip-current figures are not board measurements. Sleep should remain opt-in during future bring-up. [Sleep API](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-reference/system/sleep_modes.html), [Power-management API](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-reference/system/power_management.html)

## OTA recommendation after firmware replacement is requested

Use two app slots (`ota_0`, `ota_1`) plus `otadata` when actual flash capacity and application size permit. Write to the inactive slot, verify the image, select it, then confirm health after its first boot using the IDF rollback state machine. Enabling rollback and having a previous valid app are required for the recovery behavior. Transport authentication and image authenticity need explicit design; a SHA-256 checksum alone does not authenticate a publisher. Avoid routine bootloader/partition-table updates. **Anti-rollback is separate from app rollback and can write eFuses; leave it out of initial development under the owner's no-eFuse-change rule.** This investigation does not alter any partitions or OTA metadata. [OTA and rollback guide](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-reference/system/ota.html)

## Sources not treated as board evidence

Similar memory sizes, a common USB-UART VID/PID, and generic board profiles remain insufficient for identification. Here the stronger evidence is the original firmware's exact named Jingcai profile plus compatible runtime initialization and controller response. The official matching library configuration is used as a separate reference map; no community pinout or unobserved PCB revision was promoted to confirmed hardware.
