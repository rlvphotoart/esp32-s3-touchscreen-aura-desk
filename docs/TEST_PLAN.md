# Original verification results and release test plan

**2026-10-03 update:** AURA Desk 1.0.0 has been built and installed with pinned Arduino-ESP32 3.1.1, its matching high-performance SDK, `DebugLevel=none`, and two 5 MiB app slots. Serial app-only updates require a fresh verified full backup; no eFuse changes were made. Investigation results below remain historical, and the checklist defines acceptance criteria. Use [release validation](RELEASE_VALIDATION.md) for measured AURA outcomes and remaining limits, alongside the [user manual](AURA_DESK.md) and [build guide](FIRMWARE_BUILD.md).

The original inspection-only phase occurred on 3 October 2026, before custom firmware was built or installed. Test outcomes below are limited to that recorded evidence; a short clean boot is not a ten-boot or endurance result. Implementation, cached provider data, software snapshots, physical interaction, and update/rollback tests must be reported according to the evidence each provides.

## Completed investigation checks

| Check | Result | Evidence / limit |
| --- | --- | --- |
| USB → serial association | PASS | Registry ancestry, `1A86:7523`, pySerial and matching ROM response |
| Chip/revision/crystal | PASS | ESP32-S3 v0.2, QFN56, 40 MHz |
| Physical flash capacity | PASS | JEDEC `68 40 18`; 16 MiB |
| PSRAM identity/capacity | PASS for identification and original runtime report | Embedded 8 MiB AP_3v3; initialized runtime report; no stress test |
| Security readout | PASS | ROM and filtered non-key eFuse evidence |
| Partition decoding | PASS | Original table MD5 and 16 MB capacity bounds valid |
| Boot-region independent reads | PASS | ROM and stub 64 KiB SHA-256 identical |
| Original bootloader/application validity | PASS | esptool checksum and appended digest validate |
| Complete flash snapshot | PASS | 16 MiB, full-device MD5 comparison and local full/chunk/artifact SHA-256 checks |
| Export consistency | PASS | Exported regions and exact app image match full snapshot |
| Original board/touch startup evidence | PASS for reported startup | Board initialized/began; GT911 product/config read; visible image/touch input untested |
| Post-backup normal boot | PASS in later bounded capture | Original profile, board begin and 8 MiB PSRAM reported; one boot in 10 s, no recognized crash markers |
| Restore review | PASS, offline only | Default plan reads/verifies snapshot without opening hardware; no restore executed |
| Host publication recovery | PASS, local fixtures only | Simulated interruption after image publication recovered; corrupt partial refused and retained |
| Tool syntax/dependencies | PASS | Python compilation, Bash syntax checks, `pip check` |

## Failures and corrections retained in logs

- `system_profiler SPUSBDataType` produced no output; IORegistry exposed the device and driver ancestry.
- Full read at 460800 timed out. Sustained 230400 reads lost packets. Smaller verified reads at 115200 completed, combined with device-hash-confirmed erased regions.
- The first `espefuse summary` multi-field CLI invocation rejected argument parsing. Collection used the official public API with an explicit non-key allowlist; no burn commands were used.
- The first post-backup reset capture received zero bytes. Releasing serial control lines in the receive-only capture obtained a fresh normal boot. A later identity-check attempt without entering ROM failed as expected while the application was running; the reset tool now enters ROM briefly, verifies identity, releases BOOT/EN and boots the original application.
- Original firmware reported a GT911 address-init warning followed by successful product/config reads, and five Wi-Fi `AUTH_EXPIRE` events in the original short capture. Their causes were not diagnosed by altering configuration.

The later clean capture supersedes the empty capture as evidence of original-firmware startup. Logs are private and retained; no failed capture is counted as a clean boot.

## Custom firmware acceptance checklist

| Test | Procedure | Acceptance |
| --- | --- | --- |
| Ten boots | Ten purposeful normal boots with per-boot reset cause/version capture | All start expected image; no panic, watchdog, brownout or boot loop |
| Persistence | Write a harmless device-name/test setting in the custom namespace, reboot, read it | Exact value/schema survives; existing secrets not printed |
| Serial CLI | Exercise help/info/status/heap/uptime/version/log control; test destructive confirmation refusal | Valid responses; no secrets; destructive command cannot execute accidentally |
| Display/touch | Show color/geometry pattern and collect a bounded touch grid | Correct image/orientation, no tearing, valid touches; no sensitive GPIO changed |
| Wi-Fi | Owner-supplied network: connect, disconnect, reconnect and controlled AP loss | Valid IP/session and measured recovery; secrets not logged |
| Heap/stack | Representative UI/network load for at least 30 min; sample heaps/task high-water marks | No sustained leak or overflow; thresholds documented from measured baseline |
| PSRAM | Bounded allocation and read/write pattern test under expected UI workload | No corruption/allocation failure; keep required internal/DMA memory available |
| BLE | Discover/connect/read diagnostics and reject unauthenticated privileged writes | Correct service/state and enforced access policy |
| Recovery | Read-only ROM identification after custom app boot | Same chip/MAC accessible; original snapshot still verifies |
| OTA | Inactive-slot update, reboot, version verify; interrupted/corrupt update and unconfirmed health test | Reject corrupt/wrong image; keep valid previous app; rollback works |
| Filesystem | Only if a real filesystem partition is introduced: mount/write/reboot/read | Data persists, bounds respected; no shadow storage claim |

Ten-boot, persistence, Wi-Fi, BLE, heap endurance, full touch interaction, filesystem and OTA tests were not performed during the original inspection phase. Physical recovery restoration was also untested while the original firmware remained installed. Current AURA test outcomes belong in [RELEASE_VALIDATION.md](RELEASE_VALIDATION.md); no checklist item is a pass until its procedure has recorded evidence. BLE is outside AURA version 1 scope.
