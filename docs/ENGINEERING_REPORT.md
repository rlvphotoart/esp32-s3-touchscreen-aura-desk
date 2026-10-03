# ESP32 engineering investigation — 3 October 2026

**2026-10-03 update:** The original investigation below preceded the authorized AURA Desk replacement. AURA Desk 1.0.0 has now been built and installed with pinned Arduino-ESP32 3.1.1, its matching high-performance SDK, `DebugLevel=none`, and two 5 MiB app slots. Serial app-only updates require a fresh verified full backup; no eFuse changes were made. See the [user manual](AURA_DESK.md), [build guide](FIRMWARE_BUILD.md), and [release validation](RELEASE_VALIDATION.md) for the current implementation and measured test results.

At the end of the original investigation, the device was identified, its original firmware was preserved, and the original application booted again. The sections below retain the hardware discovery and backup assessment from that phase. Statements about unimplemented features or pending tests describe that earlier point in time.

## 1. Hardware discovered

**Confirmed:** ESP32-S3 QFN56, revision v0.2, 40 MHz crystal, dual-core 240 MHz capability, 16 MiB flash (`68 40 18`), embedded 8 MiB AP_3v3 PSRAM. The original runtime reports PSRAM initialized and 8,388,608 bytes. USB is a WCH-compatible UART bridge `1A86:7523`, product `USB Serial`, AppleUSBCHCOM, currently `/dev/cu.usbserial-10`.

**Confirmed firmware board profile / strongly inferred physical model:** Jingcai/Guition **ESP32-4848S040C_I_Y_3**. Startup and compiled DROM identify that profile; ST7701/GT911 drivers initialize and GT911 product/config registers respond. Official profile describes a 4-inch 480×480 display. Physical PCB revision/module markings remain unverified. [Hardware evidence](HARDWARE.md), [official matching profile](https://github.com/esp-arduino-libs/ESP32_Display_Panel/blob/master/docs/board/board_jingcai.md)

## 2. Existing firmware

Arduino ESP32 core 3.1.3, ESP-IDF `v5.3.2-584-g489d7a2b3a-dirty`, ESP32_Display_Panel and LVGL v8. Valid factory app at 0x10000, exact image 1,786,864 bytes; bootloader/app headers DIO / 80 MHz / 16 MB. Generic descriptor `arduino-lib-builder`, version `37d69ca`, Feb12 2025 library-build metadata; it does not identify the GUI's authoring/programming date.

Original layout: NVS 24 KiB, factory 7 MiB, coredump 64 KiB; no OTA slots or filesystem declared. Five Wi-Fi AUTH_EXPIRE events and a GT911 address-init warning were observed; the controller nevertheless returned its product/config fields. [Original firmware](ORIGINAL_FIRMWARE.md), [flash layout](FLASH_LAYOUT.md)

## 3. Backup status

**Complete verified 16 MiB snapshot:** `backups/full_flash_original.bin`. SHA-256 `18d2f07ee3d3d216ed9a1b2b83accc40d5c925cd2902f9390a8f671c0ca3a1da`. Full-device MD5 matches; local full/chunk/export hashes pass. Separate bootloader, partition, NVS, factory/app and coredump exports, decoded table, metadata and manifest are retained.

Method includes direct reads and erased regions proven by device-side hashes, then whole-device verification. Higher-baud failures and recoveries are documented. Backups/logs remain local, private and Git-ignored. [Backup record](BACKUP.md)

## 4. Security state

Secure Boot disabled; flash encryption disabled; secure download disabled; anti-rollback secure version 0; download/JTAG disable bits clear; read/write-disable masks0. No eFuse keys were exposed and no eFuse/security changes were made. Structural raw NVS CRC evidence strongly indicates standard NVS XTS-AES encryption absent in inspected current records; custom encrypted blobs and secret locations were not audited. Image integrity digests are not authenticity signatures. [Security evidence](SECURITY.md)

## 5. Development environment

Created isolated Python 3.11.9 inspection environment with official esptool 5.4.0 / pySerial 3.5 and pinned dependency lock. Existing Homebrew/Git/Python were inventoried. ESP-IDF/PlatformIO/Arduino CLI/compiler/CMake/Ninja were not found in checked locations and were not installed during the original investigation. ESP-IDF v6.1 was researched as stable at that time; SDK installation/build was deferred in that phase. The later AURA toolchain is documented separately. [Historical setup](SETUP.md), [primary-source research](RESEARCH.md), [current build](FIRMWARE_BUILD.md)

## 6. Custom firmware architecture

Proposed ESP-IDF C/C++ components: board/memory, display/touch, config/storage, diagnostics, serial CLI, Wi-Fi, optionalBLE/web, OTA and application services. Preserve the working display/touch sequence and UART recovery. This is a documented proposal, not compiled firmware. [Architecture](DEVELOPMENT.md)

## 7. Implemented features

Host-side USB detection, identity/security-checked resumable backup, private receive-only serial capture, offline snapshot verification/export, review-first guarded restoration utility and publication recovery. Hardware facts/GPIOs/capabilities/research/recovery were documented. Custom CLI, Wi-Fi manager, BLE, web management and OTA were not implemented during that original investigation. AURA later implemented serial diagnostics, Wi-Fi, HTTPS management and app OTA; BLE remains outside its version 1 scope.

## 8. Test results

Passed: ROM interrogation, independent boot-region comparison, partition/image validation, complete backup and exported-artifact verification, offline restore plan, publication-interruption/corruption checks, syntax/dependency checks and normal original-firmware startup in bounded capture. No arbitrary GPIO scanning was performed.

Failed: 460800 timeout; 230400 packet corruption; initial empty post-reset capture. Slower reads and control-line release provided successful preservation/startup. Ten boots, Wi-Fi / BLE, heap endurance, visible touch/display, OTA and physical restoration remain untested. [Test plan and evidence limits](TEST_PLAN.md)

## 9. Remaining unknowns

Physical PCB/module revision and bridge subtype; exact flash part; installed GPIO overrides vs official profile; LCD/touch visual interaction; free heap/runtime CPU/long-term PSRAM reliability; functioning Wi-Fi / BLE/network services; source/customization of bootloader and exact application/sketch origin. None is invented from compiled library strings.

## 10. Recommended next features

1. Preserve the touchscreen UI while adding measured diagnostics and a serial CLI.
2. Add a configurable Wi-Fi manager and local authenticated status, then dual-slot appOTA/rollback.
3. Add optionalBLE telemetry/provisioning after its security model is defined.
4. Add peripherals only after expansion-header routing is verified.

NativeUSB is a chip capability but conflicts with profile GPIO19 touch SDA / GPIO20 RGB data. Bluetooth Classic, built-in DAC and native 802.15.4 are absent. [GPIO reference and restrictions](GPIO_MAP.md), [capability matrix](CAPABILITIES.md)
