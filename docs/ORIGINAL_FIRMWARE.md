# Installed firmware investigation

Inspection date: 2026-10-03, Europe/Bucharest. Scope: understand the firmware already installed on the connected device. Analysis used preserved flash bytes and an earlier passive serial capture. This investigation did not install replacement firmware or initialize additional pins.

## Main finding

The existing application is an **Arduino ESP32 graphics application using ESP32_Display_Panel and an LVGL v8 port**. At boot, its board configuration identifies itself as **`Jingcai:ESP32_4848S040C_I_Y_3`**. The same board identifier is present in the application’s DROM data. This provides a credible board-model lead beyond the ESP32-S3 chip identification.

Espressif’s display-library documentation lists the corresponding **ESP32-4848S040C_I_Y_3** profile with a **480 × 480 ST7701 LCD using 3-wire SPI + RGB**, and **GT911 touch using I2C**. The installed firmware logs ST7701 and GT911 driver initialization, a successful GT911 product/configuration read, and successful board initialization/begin stages. The firmware profile is strong evidence of the intended board; physical PCB markings, revision and connector routing remain unverified. The LCD image and actual touch interaction have not been tested. [Official supported-board documentation](https://github.com/esp-arduino-libs/ESP32_Display_Panel/blob/master/docs/board/board_jingcai.md)

## Application image validation

The factory partition begins at flash offset `0x10000`. After the first 2 MiB of the full-flash read had been committed, a bounded, read-only snapshot of that prefix contained the complete application. Only the application image was extracted to a private, ignored local file, `logs/original_factory_image.bin`.

Official **esptool 5.4.0 `image-info`** successfully parsed the complete image and verified both its checksum and appended SHA-256 digest. The earlier 64 KiB `backups/application_probe.bin` contains a valid application description, but cannot validate the whole image because its first declared segment is longer than the probe.

| Field | Observed value |
|---|---|
| Target | ESP32-S3, image chip ID 9 |
| Image format | Version 1, magic `0xE9` |
| Complete application image length, including appended digest | **1,786,864 bytes** |
| Entry point | `0x403768b8` |
| Segment count | 5 |
| Image flash configuration | **16 MB, DIO, 80 MHz** |
| Image checksum | `0x63`, **valid** |
| Appended validation digest | `f7944ee33858796c4b91890aa48b7c9890399896a6e8a6a773b269833f33b88c`, **valid** |

The validation digest detects image corruption; it does not prove publisher authenticity or replace secure-boot signature verification. The full-flash backup’s completion and digest are documented separately by the backup owner. [ESP-IDF application-image format](https://docs.espressif.com/projects/esp-idf/en/v5.3.2/esp32s3/api-reference/system/app_image_format.html)

| Segment | Length | Load address | Image file offset | Memory type reported by esptool |
|---|---:|---|---|---|
| 0 | 610,980 bytes | `0x3c110020` | `0x00000018` | DROM |
| 1 | 22,908 bytes | `0x3fc96f00` | `0x000952c4` | Internal DRAM |
| 2 | 21,448 bytes | `0x40374000` | `0x0009ac48` | Internal IRAM |
| 3 | 1,075,484 bytes | `0x42000020` | `0x000a0018` | IROM |
| 4 | 55,944 bytes | `0x403793c8` | `0x001a693c` | Internal IRAM |

## Build and framework metadata

These fields come from the application’s `esp_app_desc_t`, read first from the probe with esptool’s descriptor parser and then confirmed by `image-info` on the complete extracted image.

| Descriptor field | Value |
|---|---|
| Project name | `arduino-lib-builder` |
| App version field | `37d69ca` |
| Compile date/time field | `Feb 12 2025 12:12:31` |
| ESP-IDF version field | `v5.3.2-584-g489d7a2b3a-dirty` |
| ELF SHA-256 field | `caac7d7ba088ec95ada948ea13b938829fd0c38dc9dc440203587faf20e6c98a` |
| Secure version field | `0` |

The generic `arduino-lib-builder` name and its date/version identify the recorded library build metadata. They should not be presented as the user-facing application name, the date the GUI was authored, or the date the device was programmed. No distinct application/sketch name was established.

Recognized, normalized package-path fragments in DROM identify **Arduino ESP32 core 3.1.3**; private full source paths were not copied into this report. Espressif’s official 3.1.3 release is based on ESP-IDF v5.3, consistent with the image descriptor. The boot capture references `lvgl_v8_port.cpp`, establishing an LVGL v8 port; the exact LVGL patch version and ESP32_Display_Panel package version were not established. [Arduino ESP32 3.1.3 release](https://github.com/espressif/arduino-esp32/releases/tag/3.1.3)

## Passive runtime evidence

The existing `logs/passive_115200.bin` capture is 2,866 bytes. Only explicitly recognized diagnostic fields and library/driver identifiers were examined for this report. Network names, credentials and raw log lines are omitted.

| Runtime evidence | Interpretation and limit |
|---|---|
| Board name `Jingcai:ESP32_4848S040C_I_Y_3` in initialize and begin messages | Installed firmware selects this board profile; physical hardware identity is not independently verified. |
| `Board initialize success`, `Board begin success` | The existing firmware reports completion of those startup stages. |
| `esp_lcd_st7701.c`, driver version `1.1.1` | ST7701 LCD driver was invoked at boot; visible panel output is not verified. |
| `esp_lcd_touch_gt911.c`, driver version `1.1.1` | GT911 touch driver was invoked at boot. |
| GT911 product ID `0x39,0x31,0x31`; config version `250` | The reported ID spells ASCII `911`; the driver received product and configuration register data through I2C. Actual touch coordinates/accuracy remain untested. |
| GT911 warning containing `Unable to initialize the I2C address` | A warning occurred despite a subsequent successful product/configuration read. Its cause was not established; it is not sufficient to declare the touch controller faulty. |
| `psram_initialized=yes`, `psram_bytes=8388608` | The application reports PSRAM initialization and an 8 MiB capacity. This agrees with chip interrogation, but is not a memory stress test or a measurement of remaining free heap. |
| ROM ID `esp32s3-20210327`, reset code `0x1`, boot code `0x18` | Captured boot identifiers, separate from the application build date. |
| `AUTH_EXPIRE` occurred five times | Wi-Fi authentication-expiration events were reported during this capture. The capture does not establish a connected IP session or the cause of authentication failure. |
| No recognized `Guru Meditation`, `Backtrace:` or `PANIC` markers in this short capture | No such crash marker was observed in the recorded interval; this is not a long-duration stability result. |

Espressif’s GT911 driver reads the product ID and configuration registers before printing the corresponding fields. This makes the boot read stronger evidence than merely finding the driver name in the binary. [Official GT911 driver source](https://github.com/espressif/esp-bsp/blob/master/components/lcd_touch/esp_lcd_touch_gt911/esp_lcd_touch_gt911.c)

## Static-library evidence and boundaries

A token whitelist applied only to the factory application’s DROM region confirmed `ESP32_Display_Panel`, `esp_lcd`, `lcd_st7701`, `touch_gt911`, `lvgl`, `lvgl_v8_port`, RGB-related code and the exact Jingcai board identifier. `ESP32_IO_Expander`, HTTP client, web-server, SDMMC and I2S library tokens also occur. Those additional tokens establish linked library code only; they do not prove an IO-expander chip, SD card, speaker, server or HTTP session is active.

The board profile gives a useful source for a **candidate** pin map and display timing configuration. Firmware names and public profile defaults do not independently establish the populated PCB revision, exposed header pins or all compiled GPIO assignments. Keep that distinction when documenting GPIOs or considering later firmware changes.

No NVS entry or credential was extracted. No strings from the full flash outside the factory application were searched. Private firmware and raw serial evidence remain excluded from Git by the workspace ignore rules.
