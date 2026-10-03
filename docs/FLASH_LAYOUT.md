# Original flash layout

**2026-10-03 update:** The table below is the preserved original layout, before AURA Desk installation. The current custom layout in [partitions.csv](../firmware/AuraDesk/partitions.csv) has `ota_0` at `0x20000` and `ota_1` at `0x520000`, each 5 MiB, plus NVS, OTA metadata, PHY data, LittleFS storage, and coredump. AURA uses pinned Arduino-ESP32 3.1.1/high-performance SDK and `DebugLevel=none`; serial app-only updates require a fresh verified full backup and preserve settings/cache. No eFuses changed. See the [user manual](AURA_DESK.md), [build guide](FIRMWARE_BUILD.md), and [release validation](RELEASE_VALIDATION.md).

Capacity is **16 MiB**, established by the physical flash's JEDEC ID. The existing second-stage bootloader is at `0x0000`, and the partition table was discovered at `0x8000` in preserved bytes rather than assumed. Espressif's release-pinned partition utility decodes and verifies it, including its valid table MD5 and capacity bounds.

| Start | End (inclusive) | Length | Region | Interpretation |
| --- | --- | --- | --- | --- |
| `0x000000` | `0x007FFF` | 32 KiB | Bootloader reserved region | Contains valid ESP32-S3 second-stage bootloader plus padding |
| `0x008000` | `0x008FFF` | 4 KiB | Partition-table sector | Three entries; valid table MD5 |
| `0x009000` | `0x00EFFF` | 24 KiB | `nvs`, data/NVS | Original configuration; preserved without decoding entries |
| `0x00F000` | `0x00FFFF` | 4 KiB | Unpartitioned gap | Preserved in full image; no declared use |
| `0x010000` | `0x70FFFF` | 7 MiB | `factory`, app/factory | Contains valid application and any trailing/residual bytes |
| `0x710000` | `0x71FFFF` | 64 KiB | `coredump`, data/coredump | Reserved crash-storage partition; contents preserved, not decoded |
| `0x720000` | `0xFFFFFF` | 8.875 MiB | Outside declared partitions | Not assumed empty; preserved/checked during full acquisition |

All three declared partition flags are zero. There is **no `otadata`, `ota_0`, `ota_1`, separate `phy_init`, filesystem or NVS-key partition declared**. Compiled OTA/storage library strings would not prove an active OTA layout or a mounted filesystem.

The preserved original factory application image is **1,786,864 bytes**; this is smaller than its 7 MiB partition. A valid image length does not make the remaining partition bytes disposable. The full original snapshot preserves them alongside the firmware before the subsequent authorized replacement.

## Bootloader and image information

Official esptool validates the original bootloader checksum and appended image digest. Its reported bootloader version is 1, with ESP-IDF `v5.3.2-584-g489d7a2b3a-dirty`, compile time `Feb 12 2025 12:24:09`, DIO, 80 MHz and 16 MB. These fields do not prove a source-identical unmodified upstream bootloader.

The application checksum and appended digest also validate. Both images target chip ID 9 (ESP32-S3). An appended SHA-256 validation digest is an integrity field, not a publisher signature. See [original firmware](ORIGINAL_FIRMWARE.md) and [security assessment](SECURITY.md).

## Decode again without hardware access

```sh
cd '<project-root>'
.venv/bin/python tools/vendor/gen_esp32part.py --flash-size 16MB --offset 0x8000 --primary-bootloader-offset 0x0 backups/partition_table.bin
.venv/bin/python -m esptool --chip esp32s3 image-info backups/bootloader_region.bin
```

The vendored partition utility comes from ESP-IDF v6.1; its source URL, license and SHA-256 are recorded in `tools/vendor/PROVENANCE.json`. [Official partition-table format and tool](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-guides/partition-tables.html)

No custom partition table was written during the original investigation. The subsequent authorized AURA replacement introduced the current dual-slot table; use the current build/layout files for AURA operations and this historical table when assessing or restoring the original snapshot.
