# Original architecture proposal and current firmware

**2026-10-03 update:** AURA Desk 1.0.0 is implemented, built, and installed with pinned Arduino-ESP32 3.1.1, the matching official high-performance SDK, `DebugLevel=none`, and two 5 MiB app slots. Serial app-only updates require a fresh verified full backup; no eFuse changes were made. The proposal below records the earlier investigation phase. Current implementation and measured verification are documented in the [user manual](AURA_DESK.md), [build guide](FIRMWARE_BUILD.md), and [release validation](RELEASE_VALIDATION.md).

## Historical native ESP-IDF proposal

The following architecture recommendation was written after hardware investigation, before the owner's subsequent authorization to replace the firmware. The released AURA build uses the pinned Arduino/IDF combination above; the native ESP-IDF proposal remains an alternative development path.

Use ESP-IDF C/C++, target `esp32s3`, with a pinned SDK/dependency set. Current stable research identifies v6.1, but compatibility with the intended LCD/touch/LVGL component versions must be built and tested before final selection. The original uses Arduino ESP32 core 3.1.3, an IDF 5.3-based build, ESP32_Display_Panel and LVGL v8. A migration should preserve a known working ST7701/GT911 initialization sequence and RGB timing rather than assume a generic DevKit or upgrade LVGL and every display dependency at once.

| Component | Responsibility and constraints |
| --- | --- |
| `board` | Explicit Jingcai profile, memory/strap ownership, UART recovery; no pin discovery by toggling |
| `display` / `touch` | ST7701 control+RGB timing, GT911 reads, bounded GUI event processing and LVGL locking |
| `config` / `storage` | Versioned NVS namespace/schema, settings migration and secrets outside source/Git |
| `diagnostics` | Firmware/build/chip/reset information, heap/PSRAM status, task stacks, boot counters and watchdog health |
| `cli` | UART commands for diagnostics and configuration; explicit confirmation for reset/destructive changes |
| `wifi` | Event-driven station manager, retry/backoff, RSSI/status and owner-supplied credentials |
| `ble` | Optional authenticated diagnostic/provisioning service; no privileged unauthenticated writes |
| `ota` | Inactive app-slot update, image/transport validation and boot-health rollback; no automatic eFuse anti-rollback |
| `web` | Optional local authenticated status/management, disabled until access controls are defined |
| `application` | Device-specific screens and services using events; avoid a monolithic `main.cpp` |

The initial milestone should keep the existing display/touch useful while proving a serial CLI and diagnostics. Add connectivity and dual-slot OTA after memory, heap, reboot and GPIO ownership checks. Native USB conflicts with this board's reference touch/RGB pins. Sensor/audio/CAN features require verified expansion pins and external hardware; library symbols do not establish populated components.

Proposed boot flow: board/memory initialization → configuration → diagnostics → display/touch/UI → optional connectivity → application services → health monitoring. Keep Wi-Fi callbacks, GUI state and storage writes separated by queues/events. Adopt ESP-IDF driver workarounds for rev v0.2 and use appropriate internal/DMA memory for the RGB pipeline.

A custom partition table should include NVS, otadata, two app slots, optional filesystem and coredump only after measuring the built image and choosing how to preserve original settings. Keep rollback separate from anti-rollback eFuse policy. Preserve the full original backup and the UART ROM route before any writes.

Originally proposed release gates: clean warning-reviewed build, chip/flash/partition/security validation, app-only OTA tests, 10 boots, configuration persistence, connected Wi-Fi reconnect, heap/stack endurance, display/touch interaction, and documented recovery. These are acceptance criteria, not claims that physical tests passed. See [test plan](TEST_PLAN.md) and [release validation](RELEASE_VALIDATION.md) for the actual scope and outcomes.
