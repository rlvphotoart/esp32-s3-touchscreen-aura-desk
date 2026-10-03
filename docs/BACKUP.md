# Original flash preservation

Completed on **3 October 2026 at 16:15:20 Europe/Bucharest**. The original device firmware was preserved before any replacement. No flash, partition, NVS or eFuse write commands were issued. The official volatile RAM reading stub was loaded only after the ROM/eFuse security state was assessed.

## Completed image

- File: `backups/full_flash_original.bin`
- Offset: `0x0`; length: **16,777,216 bytes (16 MiB)**
- Chip: ESP32-S3 v0.2; MAC: withheld publicly and retained in the private manifest; flash ID: `68 40 18`
- SHA-256: `18d2f07ee3d3d216ed9a1b2b83accc40d5c925cd2902f9390a8f671c0ca3a1da`
- Full-device MD5 at acquisition: `45b47b9294b417273af642fa8309ee02`, **matches saved image**
- Manifest: `backups/manifest.json`; per-file SHA-256 list: `backups/SHA256SUMS`

## Method and practical limits

The first 460800-baud bulk read failed with a serial timeout. A ROM-only 64 KiB read at 230400 succeeded, and an independent RAM-stub read of the same region matched its SHA-256 exactly. Longer 230400 reads subsequently lost packets. Valid completed data was retained; incomplete reads were not saved as valid chunks. The resumed reader switched to 115200 after corruption.

A complete validated factory application already fit within the first 2 MiB. More data existed after that application image, so its trailing partition bytes were preserved rather than discarded. To avoid unnecessary transfer of erased space through the unreliable UART link, each remaining 64 KiB region was tested with the official stub's `flash_md5sum`. A region was filled with `0xff` only if the device-computed digest exactly matched the known 64 KiB all-erased digest. Other regions were read normally through official `read_flash`, which checks each returned read against a device MD5. The final whole-flash MD5 was then compared to the complete generated image.

The completed snapshot covers every external-flash byte. It is **not a claim that every byte was physically downloaded over UART**:

| Acquisition method in manifest | Bytes |
| --- | ---: |
| Earlier directly read prefix, revalidated against device MD5 | 3,538,944 |
| Final direct reads, each device-MD5 checked | 1,376,256 |
| Device-MD5-confirmed erased `0xff` regions | 11,862,016 |
| **Total** | **16,777,216** |

SHA-256 is computed locally for the full image, chunks and exports. Device-side comparison uses the MD5 operation supplied by Espressif's reader. These integrity checks do not authenticate a publisher or replace cryptographic signature verification. They do give consistent byte-level preservation evidence. ROM bootloader code and eFuses are not stored in the external-flash image and cannot be restored from it.

## Exported artifacts

| File | Offset | Length / scope |
| --- | --- | --- |
| `bootloader_region.bin` | `0x0` | 32 KiB reserved bootloader region |
| `partition_table.bin` | `0x8000` | 4 KiB partition-table sector |
| `partition_table_decoded.txt` | — | Official verified CSV decoding |
| `nvs.bin` | `0x9000` | 24 KiB, opaque original settings |
| `factory_partition.bin` | `0x10000` | Complete 7 MiB partition, including trailing bytes |
| `application_image.bin` | `0x10000` | Valid exact image, 1,786,864 bytes |
| `coredump.bin` | `0x710000` | 64 KiB, preserved without interpreting memory contents |
| `chip_info.txt`, `flash_info.txt`, `security_info.txt` | — | Acquisition evidence |
| `efuse_summary_filtered.json` | — | Allowlisted non-key fields only |

Each export was compared to the verified full image. The bootloader/application checksum and appended image digests validate through `esptool image-info`; the partition table's MD5 and capacity bounds validate through Espressif's partition utility.

## Reuse and interrupted acquisition

`./scripts/verify_backup.sh` checks the ORIGINAL snapshot offline. A different snapshot directory can be supplied as its argument. `./scripts/backup_flash.sh` requires a privately supplied `AURA_EXPECTED_MAC` and creates a fresh dated directory, displays the port, checks the same chip/MAC/flash/security and acquires another snapshot at conservative 115200 baud.

If an acquisition fails, keep the `.partial` file. A resume requires that exact board and a device-MD5 match for its entire saved prefix:

```sh
.venv/bin/python tools/backup_device.py --port /dev/cu.usbserial-10 --output-directory /absolute/path/to/incomplete-snapshot --baud 115200 --resume --verify-erased
```

Final publication uses a private, fsynced `manifest.json.pending` commit record. It keeps the complete partial image until both final image and manifest are published without clobbering other files. If interrupted at publication, `--recover-commit` validates the recorded full image and finishes publication **offline**:

```sh
.venv/bin/python tools/backup_device.py --output-directory /absolute/path/to/snapshot --recover-commit
```

The host-only interrupted-publication path and corrupted-image refusal were exercised with temporary fixtures. No synthetic fixture or fake device data was used in the ORIGINAL snapshot.

Backups/logs are Git-ignored; directories are mode 0700 and private evidence files mode 0600. They may contain private configuration or prior crash memory. Do not upload them as routine troubleshooting attachments.
