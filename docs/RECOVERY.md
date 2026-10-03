# Recovery plan for this device

No restoration or destructive recovery test was performed during identification. The original flash was preserved privately before the subsequent AURA installation. Reading ROM identity, security fields and flash demonstrates that the automatic ROM download path is accessible.

## Recognize the target

Run `./scripts/detect_device.sh`. The observed UART bridge is `1A86:7523`, currently `/dev/cu.usbserial-10`; port names can change after reconnection. Descriptor matching selects only one matching bridge and refuses ambiguity. Chip/MAC/flash checks must identify ESP32-S3, the privately supplied `AURA_EXPECTED_MAC`, JEDEC `68 40 18`, 16 MiB. USB descriptors alone cannot distinguish two identical boards.

## Download mode

The observed bridge's DTR/RTS automatic reset sequence works with official esptool. It changes reset/boot state, not flash contents. For manual recovery, ESP32-S3 joint download boot requires GPIO0 low and GPIO46 low while EN/CHIP_PU is reset. Use board-labeled BOOT and RESET/EN controls only after identifying those controls; their physical locations were not inspected here. Release BOOT after esptool connects. Never short an unverified header pin to enter boot mode.

The reference display profile uses GPIO0/46 as RGB signals after boot. Its native USB pins are already used by touch/LCD. Use the proven UART bridge for recovery. [Espressif boot-mode selection](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html)

## Verify and review the original restore

```sh
cd '/absolute/path/to/ESP32'
export AURA_EXPECTED_MAC='<your verified six-octet MAC>'
./scripts/verify_backup.sh
./scripts/restore_original.sh
```

Both default commands operate on the original `backups/` snapshot. The restore wrapper prints a **review-only plan and does not open hardware** unless explicitly invoked with `--execute`. For another saved snapshot, verification accepts a directory argument and the restore tool accepts `--directory /absolute/path/to/snapshot`.

An explicit restore is destructive to the current external-flash contents. It restores all 16 MiB, including the bootloader, partition table, application, NVS, crash storage and unnamed areas. The tool requires both `--execute` and the exact `--confirm-mac "$AURA_EXPECTED_MAC"`. It first creates and verifies a fresh `backups/pre-restore-*` current-state snapshot, then rechecks chip/MAC/flash/security, writes the original at offset zero, checks the device MD5, and resets to normal boot. It retains original mode/frequency/size and has no eFuse write or security-bypass path.

No `erase-flash` command is used. **Writing flash automatically erases the addressed sectors**, so the restore remains destructive even without a separate erase command. The execution path is prepared and locally reviewed; it has not been tested by restoring this board during the initial investigation; later AURA installations do not establish a successful original-firmware restore.

## Failed firmware or partition table

If a future image fails to boot, enter ROM download mode using the UART bridge, verify the local original snapshot, and review the restore plan. ROM bootloader access is independent of the application and custom partition table when download mode remains enabled. Do not burn security or download-disable fuses during early development. Restoring external flash cannot undo an eFuse change.

For future NVS-only troubleshooting, first preserve the current full flash and identify the **current** partition table; offsets may differ after a future custom build. The original NVS range is `0x9000` for `0x6000` bytes, but no script automatically clears it. Erasing only NVS loses saved configuration and is a separate explicit maintenance decision.

## Serial reliability

The bridge timed out at 460800 baud and dropped packets in sustained 230400 reads. Use 115200 baud as the conservative maintenance default. Close other serial clients; wrapper captures acquire exclusive access. A fresh backup supports resuming only after the stored prefix matches the device MD5. Preserve incomplete `.partial` files as incomplete evidence, not as recoverable full images. See `BACKUP.md` for acquisition and integrity details. [Official esptool troubleshooting](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/troubleshooting.html)
