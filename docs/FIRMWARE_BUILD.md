# Aura Desk firmware build

**2026-10-03 update:** AURA Desk 1.0.2 has been built and installed using pinned Arduino-ESP32 3.1.1 and the matching official high-performance SDK. Release builds use `DebugLevel=none` and two 5 MiB application slots. Serial app-only updates require a fresh verified full-flash backup and preserve settings/cache; no eFuse changes were made. See the [user manual](AURA_DESK.md) and [release validation](RELEASE_VALIDATION.md) for current behavior and recorded device tests. Network, physical touch, and OTA results depend on those tests.

The build uses a local Arduino CLI installation and isolated SDK/libraries under `.toolchains/`. Global Arduino installations and shell configuration are not used. The exact versions, upstream commits, artifact URLs, checksums, and board parameters are retained in [TOOLCHAIN_LOCK.json](TOOLCHAIN_LOCK.json).

## Build the application

From the workspace root:

```sh
./scripts/build.sh
```

Before compilation the wrapper checks the original reading catalog and the generated 500-service browser include against their reviewed public JSON sources. The generated include is an adjacent C++ raw-string literal in the flash-resident HTML; it is not parsed or rebuilt in device heap memory.

The wrapper reads the release version from `firmware/AuraDesk/firmware_version.h`. It runs compilation with four workers and writes intermediate files to `build/AuraDesk/` and exported artifacts to `releases/aura-desk-<version>/`. It requires complete sources, a custom partition table, the correct supported-board configuration, and the matching high-performance SDK with XIP from PSRAM. It does not open a serial connection, erase, upload, or reset a device. Hardware installation and release verification are separate operations.

Generated ELF/map files support crash diagnosis. The wrapper replaces Arduino3.1.1's incorrect default merged image with an explicitly verified16MiB image: bootloader at0x0, partition table at0x8000, and application at0x20000. It checks the compiled table against the source CSV, partition ranges, both OTA-slot capacities, image checksums/digests, and the complete merged contents. `build-layout.json` records offsets and SHA-256 hashes. No `boot_app0.bin` is included; the OTA metadata remains erased, and the bootloader selects the first OTA slot.

**Never use Arduino CLI upload or its uncorrected default merged binary for this custom layout.** Arduino3.1.1 hardcodes application0x10000 and boot_app0xE000 despite our partition CSV. Device installation must use the explicit offsets in the validated build layout. OTA accepts only `AuraDesk.ino.bin`, the application image for the inactive partition; the full merged image is not an OTA file.

For a serial application update of the known initial `ota_0` installation, `tools/flash_aura.py --app-only --execute` requires a freshly acquired backup whose whole-device MD5 still matches live flash. It also checks matching bootloader/partition bytes and erased OTA metadata or CRC-valid sequence 1 in `VALID` state. It writes only the application at `0x20000`, preserves the last sector's unchanged tail, and verifies the complete 16 MiB against the backup plus new application. It rejects `--erase-all` and other OTA-slot/update states. Full initial installation remains a separate explicit erase operation.

## Pinned dependencies

| Component | Version or pin | Purpose |
| --- | --- | --- |
| Arduino CLI | 1.5.1, macOS arm64 | Isolated compilation orchestrator |
| Arduino-ESP32 | 3.1.1 | Framework, networking, FreeRTOS and IDF integration |
| Official high-performance SDK | esp32-3.1.1-h | RGB reliability during flash operations, 64-byte cache lines, PSRAM XIP |
| ESP32_Display_Panel | Commit `92b790ed6d24b0678e2f45b1fc85f0abd2d41b33`; metadata 1.0.5 | Exact Jingcai board, ST7701 display and GT911 touch drivers |
| ESP32_IO_Expander | 1.1.0 | Display library dependency; expander not enabled on this board |
| esp-lib-utils | 0.2.0 | Driver logging and utilities |
| LVGL | 8.4.0 | Touchscreen interface, fonts, keyboard and snapshots |
| ArduinoJson | 7.4.2 | API/configuration JSON processing |

The panel repository has no v1.0.5 tag despite its metadata; use the exact commit. Do not substitute current library releases without a compatibility build and runtime verification.

## Reproducing the local toolchain

The dependency lock contains the verified archive hashes. Download Arduino CLI from its pinned release URL, check its SHA-256 against the lock, then extract `arduino-cli` into `.toolchains/bin/`. Create these directories:

```sh
mkdir -p .toolchains/bin .toolchains/arduino/data \
  .toolchains/arduino/downloads .toolchains/arduino/user/libraries
```

Create `.toolchains/arduino-cli.yaml` using absolute paths for the current checkout:

```yaml
board_manager:
  additional_urls:
    - https://espressif.github.io/arduino-esp32/package_esp32_index.json
directories:
  data: /absolute/path/to/ESP32/.toolchains/arduino/data
  downloads: /absolute/path/to/ESP32/.toolchains/arduino/downloads
  user: /absolute/path/to/ESP32/.toolchains/arduino/user
```

Install the pinned core:

```sh
.toolchains/bin/arduino-cli --config-file .toolchains/arduino-cli.yaml core update-index
.toolchains/bin/arduino-cli --config-file .toolchains/arduino-cli.yaml core install esp32:esp32@3.1.1
```

Arduino CLI verifies the core/tool archive checksums from the official package index. The high-performance SDK is an explicit additional dependency: download the exact URL in the lock and verify its SHA-256 before extracting. It replaces only the `esp32s3/` tree under `.toolchains/arduino/data/packages/esp32/tools/esp32-arduino-libs/idf-release_v5.3-cfea4f7c-v1/`. Preserve the original tree separately. The inspected archive's top directory is `arduino-esp32-libs-all-release_v5.3-cfea4f7c98/`; strip that prefix when copying its ESP32-S3 contents. Do not combine this SDK with a different Arduino-ESP32 core version. [Official SDK replacement instructions](https://github.com/esp-arduino-libs/arduino-esp32-sdk)

Clone each library repository listed in the lock into `.toolchains/arduino/user/libraries/` using its listed library name. Check out its exact commit; for shallow clones, fetch the required commit explicitly. Confirm the final checked-out hash with `git rev-parse HEAD`. The full commits, rather than mutable branch names, are the reproducibility contract.

The existing `firmware/AuraDesk/lvgl_v8_port.cpp`, `lvgl_v8_port.h`, and `lv_conf.h` originate from the pinned panel library's official `examples/arduino/gui/lvgl_v8/simple_port/`. The port is retained under its CC0-1.0 license, with local changes for direct-mode anti-tearing. The application LVGL configuration enables RGB565 without byte swapping, Montserrat fonts 14/16/20/24/32/48, default font16, keyboard, and snapshots.

## Board and memory configuration

The wrapper defines `NETWORK_EVENTS_MUTEX` for every C++ translation unit, including the Arduino Network library. Core 3.1.1 otherwise iterates and mutates its callback vector without synchronization. Repeated device boots exposed an invalid callback target during registration. AURA registers its filtered disconnect callback before enabling Wi-Fi, and the framework mutex protects both application and internal startup registrations. Do not define this flag only in the sketch: it changes the NetworkEvents class layout and must be consistent across all C++ units. AURA keeps station mode enabled and its callback only records the disconnect reason; it never adds/removes callbacks from within event delivery.

The firmware selects `BOARD_JINGCAI_ESP32_4848S040C_I_Y_3`: 480×480 ST7701 over control SPI plus 16-bit RGB, GT911 over I2C, and PWM backlight. Flash is DIO80MHz, 16MiB; PSRAM is OPI80MHz, 8MiB; CPU frequency is 240MHz. UART remains the console/recovery transport. Native USB GPIO19/20 are already assigned to touch/display by the board profile.

The UI uses the official LVGL direct-mode port with two full frame buffers in PSRAM. RGB bounce-buffer size is expressed in pixels; `480 * 10` consumes approximately 19.2KiB internal RAM for its two RGB565 buffers. The LCD and LVGL tasks run on the same main core. Use the pinned board's vendor initialization commands and timings instead of a generic ST7701 initialization.

The official high-performance SDK has XIP from PSRAM enabled. This avoids the known RGB starvation risk while SPI flash operations temporarily disable external-memory cache. Actual NVS writes and OTA still require device verification. [Espressif RGB drift guidance](https://github.com/esp-arduino-libs/ESP32_Display_Panel/blob/92b790ed6d24b0678e2f45b1fc85f0abd2d41b33/docs/envs/use_with_arduino.md#solution-for-screen-drift-issue-when-using-esp32-s3-to-drive-rgb-lcd-in-arduino-ide)

Use `esp_psram_get_size()` to check physical PSRAM capacity. With XIP enabled, `ESP.getPsramSize()` reports the smaller usable PSRAM heap after instruction/read-only mappings; a value below 8 MiB does not mean the physical chip is undersized.

## OTA validation and screenshot capture

The SDK enables application rollback. Arduino core3.1.1 normally validates a pending update inside `initArduino()` before application `setup()`. Override its weak hook with C linkage so the application can perform its own startup health checks:

```cpp
extern "C" bool verifyRollbackLater(void) {
    return true;
}
```

Only after display/touch, UI, services, and startup checks succeed should the application call `esp_ota_mark_app_valid_cancel_rollback()`. [Pinned Arduino initialization source](https://github.com/espressif/arduino-esp32/blob/3.1.1/cores/esp32/esp32-hal-misc.c)

LVGL8.4 snapshot support provides `lv_snapshot_buf_size_needed()` and `lv_snapshot_take_to_buf()`. Capture `LV_IMG_CF_TRUE_COLOR` into a buffer sized by the first function, preferably in PSRAM. Hold the LVGL mutex during capture, then release it before streaming the copied buffer. A 480×480 RGB565 image contains 460800 pixel bytes; use LVGL's reported buffer size for alignment and any object draw extent. Snapshot generation confirms the software-rendered UI; it does not prove physical panel colours, orientation or touch accuracy.

Release builds suppress Arduino diagnostic logging during binary transfers. The screenshot header includes the SHA-256 of the actual pixel bytes. The decoder requires the exact payload length, terminator, and matching digest, and rejects diagnostic text inserted into the stream. The UART client waits through a possible WCH driver reset before sending a command.

## Public artifact paths

C and C++ builds use `-ffile-prefix-map` and `-fdebug-prefix-map` to replace the checkout path with `.` in compiled file names and debug metadata. Linker map paths are normalized separately. The wrapper rejects any exported binary, ELF or map containing the current home path. Application/merged images are revalidated after building, and release packages are checked before publication. Private backups and captures are excluded.
