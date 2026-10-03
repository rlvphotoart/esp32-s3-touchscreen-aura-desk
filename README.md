# AURA Desk

This source-history snapshot omits local firmware binaries, private recovery backups, and live device captures. Paths to those historical local artifacts are retained as documentation rather than public downloads.

Custom internet-dashboard firmware for the connected ESP32-S3 touchscreen. The original **Horizon** interface is designed for its 480 × 480 display, with an ivory canvas, ink-blue navigation, cobalt actions, large touch targets, and clear offline states.

The original firmware was backed up again and verified before a complete flash erase and AURA installation. Later refinements preserve saved configuration. Installation and live checks are recorded in [release validation](docs/RELEASE_VALIDATION.md); original investigation documents retain their historical scope.

## Functions

- Touchscreen setup for a 2.4 GHz router, saved credentials, automatic reconnection, and network scanning.
- Network clock/calendar, editable city, and daylight-saving rules for supported regions.
- Open-Meteo weather, three forecast days, sunrise/sunset, European AQI, and PM2.5.
- Dated ECB EUR/RON and EUR/USD reference rates.
- Two configurable public HTTPS JSON API widgets with dot-path fields and controlled refresh intervals.
- Focus timer, countdowns, and stopwatch using monotonic time.
- Brightness control, inactivity dimming, diagnostics, and private UART status.
- Local HTTPS browser management, screen pairing, settings export, and dual-slot application updates.

Readings retain their source dates and data ages. Invalid API values remain unavailable. Renderer fixtures are confined to the separate host QA program and are not linked into the target application.

## First use

Open **Settings → Network** to connect or change the router. Select its **2.4 GHz** network, enter the password on the touchscreen, and tap **Connect**. Internet data and the clock refresh automatically after time synchronization. Bucharest is the editable initial city; change it in **Settings → Location**.

Open **Settings → Browser configuration** for the local HTTPS address and six-digit pairing code. Pair a browser on the same network to configure API widgets, export non-secret settings, or install a matching application update. The device uses its own local certificate; use the address displayed on its screen.

Complete instructions and implemented limits: [AURA Desk user manual](docs/AURA_DESK.md).

## Release and source

releases/aura-desk-1.0.1 (`releases/aura-desk-1.0.1`; historical local artifact omitted from public history) contains:

- `AuraDesk.ino.bin` — application image for browser OTA.
- `AuraDesk.ino.merged.bin` — complete 16 MiB factory image.
- `build-layout.json` — exact flash offsets, sizes, and image SHA-256 hashes.
- `TOOLCHAIN_LOCK.json` — pinned framework, SDK, drivers, and UI dependencies.
- `release-manifest.json` and `SHA256SUMS` — source and packaged-release integrity records.

The source is in [firmware/AuraDesk](firmware/AuraDesk). Host-rendered screens and device framebuffer captures are in artifacts (`artifacts`; historical local artifact omitted from public history). [UI QA](docs/UI_QA.md) distinguishes synthetic fixture previews from live device evidence.

## Hardware and build

| Item | Confirmed target |
| --- | --- |
| MCU | ESP32-S3 QFN56 revision v0.2; 240 MHz application clock |
| Memory | 16 MiB flash; physical 8 MiB OPI PSRAM |
| Board profile | Jingcai ESP32-4848S040C_I_Y_3 |
| Display | ST7701 RGB + three-wire SPI, 480 × 480 |
| Touch | GT911 I2C, runtime ID `911` |
| USB-UART | WCH-compatible bridge; `/dev/cu.usbserial-10` on this Mac |
| Layout | Two 5 MiB OTA slots, settings, LittleFS cache, coredump |

The physical PCB revision remains unverified. Drivers use the profile established by the working original firmware and live device initialization. Native USB pins overlap this board's display/touch wiring; use its USB-UART bridge.

Arduino-ESP32 **3.1.1**, its matching official high-performance SDK, ESP32_Display_Panel, LVGL **8.4.0**, and ArduinoJson **7.4.2** are pinned locally. XIP reserves some physical PSRAM for executable code, so usable heap PSRAM is smaller than 8 MiB. [Build details](docs/FIRMWARE_BUILD.md)

```sh
cd '<project-root>'
./scripts/build.sh
./scripts/verify_backup.sh
./scripts/restore_original.sh       # review only
```

Do not use ordinary Arduino CLI upload: its default merged-image offsets differ from this custom layout. The installer verifies device identity, a fresh backup, layout, and whole installed flash. Its `--app-only` option is limited to a known initial AURA ota0 installation; use browser OTA after slot changes. [Recovery](docs/RECOVERY.md)

## Original backup

The complete original external flash is retained privately at `backups/full_flash_original.bin` and the fresh pre-install snapshot (`backups/pre-aura-20261003/full_flash_original.bin`; historical local artifact omitted from public history), with manifests and full-device MD5 verification. Size: **16,777,216 bytes**. SHA-256:

```text
18d2f07ee3d3d216ed9a1b2b83accc40d5c925cd2902f9390a8f671c0ca3a1da
```

Bootloader, partition table, NVS, original application, and coredump exports are also retained. Backups and raw captures can contain private configuration; they are excluded from Git and the shareable package. Secure Boot, flash-encryption, and anti-rollback eFuses were not changed.

## Evidence and documentation

- [Release validation](docs/RELEASE_VALIDATION.md), [user manual](docs/AURA_DESK.md), [UI QA](docs/UI_QA.md).
- [Build](docs/FIRMWARE_BUILD.md), [dependency lock](docs/TOOLCHAIN_LOCK.json), [license notices](THIRD_PARTY_NOTICES.md).
- [Hardware](docs/HARDWARE.md), [GPIO map](docs/GPIO_MAP.md), [original firmware](docs/ORIGINAL_FIRMWARE.md).
- [Backup evidence](docs/BACKUP.md), [original flash map](docs/FLASH_LAYOUT.md), [security](docs/SECURITY.md), [recovery](docs/RECOVERY.md).

The application and UX are original custom source. Platform and library components retain their upstream licenses. Physical panel appearance and manual touch usability are separate from successful controller initialization and software-rendered screenshot verification.


Version 1.0.1 adds a saved Always-on display switch in touchscreen and browser Settings. On retains chosen brightness; Off dims after three minutes. This historical firmware source snapshot is recovered from retained build inputs.
