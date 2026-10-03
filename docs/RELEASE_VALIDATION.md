# AURA Desk 1.0.0 — release validation

This source-history snapshot omits local firmware binaries, private recovery backups, and live device captures. Paths to those historical local artifacts are retained as documentation rather than public downloads.

Validated on 2026-10-03 against the connected ESP32-S3 touchscreen. The final application is installed and running; this report separates live device evidence from host UI tests and remaining physical observations.

## Installed release

| Item | Result |
| --- | --- |
| Product / interface | AURA Desk 1.0.0 / original Horizon UX |
| Target | ESP32-S3 rev v0.2; Jingcai ESP32-4848S040C_I_Y_3 profile |
| Memory | 16 MiB flash; physical 8 MiB OPI PSRAM |
| Display / touch initialization | ST7701 RGB 480 × 480; GT911 runtime ID `911` |
| Application image | 1,923,024 bytes; fits both 5 MiB slots |
| Active application after browser update | `ota_1`, offset `0x520000`, sequence 2, state `VALID` |
| Previous application | `ota_0`; same verified release image, state `VALID` |
| Security provisioning | Secure Boot/flash encryption disabled; no eFuse writes |

Application SHA-256:

```text
18a0d6f6646f8bc5c3263bbc472310697774b14a1c7e6972755681f4b797f1b2
```

Factory merged-image SHA-256:

```text
8ec04019f462b2c6009047476653766d91074e98536bef79aff8f06463a2d6b1
```

The factory image contains erased settings/cache/OTA metadata. The running device retains its configured settings and live data and has accepted a browser update, so its current whole-flash contents intentionally differ from that factory image. The serial refinements verified all 16 MiB against the expected application overlay with every other byte preserved. The later OTA readback separately verified the image in both application slots and the active slot's accepted metadata.

## Verification results

| Check | Result and scope |
| --- | --- |
| Original backup | Fresh pre-erase 16 MiB snapshot; block hashes and complete device MD5 verified; identical to the earlier original snapshot |
| Initial installation | Full external-flash erase and explicit bootloader/table/application writes; complete 16 MiB image verified before boot |
| Final serial refinements | Fresh current-state backup, identity/security checks, application-only writes, unchanged sector tail, whole-device MD5 verification |
| Target build | Pinned toolchain; compiled images/checksums/digests/table/custom merged offsets validated |
| Startup stability | **10 consecutive final-image boots after OTA**; one ROM boot each; display/UI and startup health passed; no Guru Meditation, backtrace, panic, brownout, or fatal markers |
| Memory | Lowest reported minimum heap during this boot run: **107,076 bytes**; physical PSRAM checked independently of XIP-reserved heap |
| Router and time | Live router connection and synchronized clock verified over UART and authenticated HTTPS |
| Public providers | Real Open-Meteo weather, air quality, and dated ECB rates returned valid finite readings with confirmed data ages |
| HTTPS browser | Real device page loaded; pairing succeeded; secure/HttpOnly/SameSite cookie checked; every request used the same pinned device certificate |
| Access checks | Unauthenticated status rejected with HTTP 401; invalid CSRF rejected with HTTP 403 |
| Settings export | Authenticated export succeeded and excluded passwords, pairing codes, session/CSRF data, and TLS private keys |
| Custom JSON widget | Public HTTPS JSON field configured, fetched, displayed as a finite humidity percentage, and restored to disabled defaults because the initial widget was unconfigured |
| Browser OTA | Application uploaded to inactive slot, verified by the device, restarted, and passed application startup health |
| OTA flash readback | CRC-valid sequence 2 in state `VALID`; active `ota_1`; device MD5 for both application images equals the release image MD5 |
| Actual screens | Home, Weather, Tools: exact 480 × 480 RGB565 snapshots; length, terminator, and device SHA-256 verified before PNG conversion; all inspected |
| Host UI | All 14 real LVGL pages rendered; keyboard, reveal/masking, text preservation, UTF-8 limits, action dispatch, timer pause/start, and cached-age labels checked |
| Tool/package hygiene | Python syntax, shell syntax, dependency consistency, explicit package allowlist, artifact hashes, and archive byte/CRC checks |

Private raw logs and device snapshots remain under `logs/` and `backups/`, outside the shareable archive. The public conclusions are in [RELEASE_VALIDATION.json](RELEASE_VALIDATION.json).

## Actual device screens

These images are decoded from the running firmware's checked framebuffer transfer. They contain actual API values, not renderer fixture values.

Home: `../artifacts/device-home.png` (historical local capture; omitted from public history)

Weather: `../artifacts/device-weather.png` (historical local capture; omitted from public history)

Tools: `../artifacts/device-tools.png` (historical local capture; omitted from public history)

## Corrections made during release testing

The high-performance SDK maps code/read-only data into PSRAM. Startup now checks physical capacity with `esp_psram_get_size()` rather than confusing its smaller usable heap with a smaller physical chip.

Repeated boots exposed a Wi-Fi callback-vector race in Arduino core 3.1.1. The release registers its filtered callback before starting Wi-Fi and enables `NETWORK_EVENTS_MUTEX` across all C++ units, including the rebuilt Network library. The corrected image subsequently passed the ten-boot run and live network/OTA checks. Future callbacks must not mutate registrations or disable STA while the nonrecursive event mutex is held.

An Arduino diagnostic warning interrupted an early binary screenshot. Release diagnostic logging is quiet; captures now carry a pixel SHA-256 and the decoder rejects extra bytes or a mismatching hash. All release screenshots passed these checks.

API/cache parsing rejects incomplete or malformed readings. Valid cached values with an unavailable age are labelled saved data; they are not presented as waiting for their first-ever update. Host fixture values remain outside the target sketch.

## Practical limits

Controller initialization and software-rendered screenshots do not establish physical panel colour accuracy, orientation by inspection, or touch feel/accuracy across the glass. Those require hands-on observation. No external sensors or audio hardware were connected or assumed.

Successful OTA installation, image readback and startup acceptance were exercised. Forced failed-update rollback, deliberate power interruption, prolonged burn-in, all router security modes, unsupported international timezones, and every possible third-party API were not tested. The implementation's actual scope and supported router/API formats are documented in [the user manual](AURA_DESK.md).

The original full-flash backup is retained privately with SHA-256 `18d2f07ee3d3d216ed9a1b2b83accc40d5c925cd2902f9390a8f671c0ca3a1da`. Restoring it was not performed. The archive's SHA-256 hashes establish integrity; they are not a publisher signature.
