# AURA Desk 1.0.3 — release validation

Validated on 2026-10-03 against the connected ESP32-S3 / Jingcai ESP32-4848S040C_I_Y_3 touchscreen. The final 1.0.3 image is installed, read back and accepted. Both custom API readings appear directly on Home and in Your data. Native Safari pairing, configuration, error feedback, refresh, export and OTA were exercised.

## Installed images

| Item | Result |
| --- | --- |
| Application | 1,939,536 bytes; fits both 5 MiB slots |
| Active image | ota_1, offset 0x520000, sequence 6, VALID |
| Previous image | ota_0, accepted private preliminary 1.0.3 candidate retained |
| Backup | Fresh complete 16 MiB pre-final-update snapshot; full device MD5 verified |
| Installation | Native Safari paired HTTPS application OTA; verified reply and restart observed |
| Configuration | Both saved widgets, current brightness 49% and Always-on retained |
| Irreversible security changes | No eFuse writes; Secure Boot and flash encryption unchanged |

Application SHA-256: `544c77cd798d1ea0f4e43965acd85ef2b9a2d19f623fee94e996de70ab065c9b`.

Factory merged-image SHA-256: `e45b4395c472401369933f1faeab10f6d23605ad48f695720d566e8a74f1e0d4`.

Pre-final-update backup SHA-256: `f97ea258bdf338d207deee7cf196ce67df2ebb90180f854f3a5427449fabb12b`. Full backups and device captures remain private.

## Behavior and checks

| Check | Result and scope |
| --- | --- |
| API Home visibility | Two real Home regions independently match each saved label, current scalar value and unit |
| Full API detail values | Two real Your data regions independently match full values/units; both latest refreshes HTTP 200, no error |
| Device display/settings | Authenticated HTTPS and UART confirm unchanged widget configurations, Always-on and current 49% backlight; verifier leaves Home displayed |
| Native Safari | Final pairing and persistent wrong-code error; saved Bitcoin/humidity forms; malformed-path inline rejection; refresh, reload, settings save/export and final application OTA |
| Real provider errors | Earlier private candidate reports missing JSON fields and real HTTP 429; retains the last successful value/age while the other widget remains valid |
| C++ widget host tests | 125 actual-source assertions with controlled platform/HTTPS stubs: validation, arrays/scalars/zero, request/errors and retained readings |
| Browser host tests | 56 assertions against exact embedded JavaScript: ready examples, edits, feedback, session expiry, polling and fetch/body deadlines |
| HTTP response host tests | 17 actual-source assertions for headers, complete-send-before-close and failure propagation |
| Actual LVGL host | All 14 pages and both display modes; Home tile pointer targets, full/compact values, Saved/error states, Home/Settings return routes, disabled shortcut and model updates |
| Earlier regressions retained | Timer countdown-to-Focus/presets, five Browser reopen cycles, Settings scroll, credentials/keyboard and monotonic timers pass |
| Flash readback | Both OTA-slot MD5 readbacks match the final and private preliminary images; active sequence 6 is CRC valid and accepted |
| Final startup checks | Three consecutive boots; one ROM boot each; display/UI/startup health pass; zero crash markers; lowest reported startup minimum heap 101,296 bytes |
| Public image hygiene | Owner home paths absent from application/merged/ELF/map; factory image storage gaps are erased |
| Public source/package | Explicit public allowlist; no private device configuration, backup, raw capture or owner identity in published files |
| Licenses | 22 full upstream texts and font/notice provenance included; original source/UX rights retained |

The first screen-verification attempt used the prior 80% baseline and stopped when the device reported its current 49% brightness. A waiting retry using 80% was stopped; the complete verification using the current 49% setting passed. No display-policy firmware change was made. The final saved Bitcoin source uses Coinbase because CoinMarketCap returned HTTP 429 after the test reboots. The CoinMarketCap preset remains available.

Native Safari interactions, earlier candidate failure checks and final device evidence are distinguished in [BROWSER_API_VALIDATION.md](BROWSER_API_VALIDATION.md) and [its structured conclusions](BROWSER_API_VALIDATION.json). The final read-only screen verifier performs ROM identity checks, pinned HTTPS pairing, SHA-256-framed pixel transfer and private regional OCR. Its report contains conclusions only. Concurrent Safari interactions exercise the web interface; the verifier itself does not write settings, flash or eFuses.

[Structured release conclusions](RELEASE_VALIDATION_1.0.3.json). Historical reports for [1.0.0](RELEASE_VALIDATION_1.0.0.md), [1.0.1](RELEASE_VALIDATION_1.0.1.md) and [1.0.2](RELEASE_VALIDATION_1.0.2.md) retain the earlier ten-boot, full network/API, real three-minute dim/Always-on and timer/Browser results.

## Public previews and limits

Public previews are offline host renders of the real LVGL source. Live screen images, local addresses, pairing material, certificates and sessions are excluded from source and release packages.

![Offline Home](../artifacts/ui-preview/home_offline.png)

Host tests exercise actual LVGL pointer hit-testing. Device checks use UART page navigation and actual framebuffer/HTTPS data. Physical finger taps, optical brightness/color, forced rollback, deliberate power interruption and prolonged burn-in were not measured in this release run. SHA-256 files establish integrity and are not publisher signatures.
