# AURA Desk 1.0.4 — release validation

Validated on 2026-10-03 against the connected ESP32-S3 / Jingcai ESP32-4848S040C_I_Y_3 touchscreen. The final **1.0.4** image is installed, read back and accepted. Both Browser dropdowns contain 100 searchable public API presets from 19 providers in 17 categories. Native Safari Save actions produced successful real ESP32 readings from representative new sources, and both configured widgets are visible on Home and in Your data.

## Installed images

| Item | Result |
| --- | --- |
| Application | 1,984,352 bytes; fits both 5 MiB slots |
| Active image | ota_0, offset 0x20000, sequence 7, VALID |
| Previous image | ota_1, accepted final public 1.0.3 image retained |
| Backup | Fresh complete 16 MiB pre-update snapshot; full device MD5 verified |
| Installation | Paired, certificate-pinned local HTTPS application OTA; healthy restart and preserved settings verified |
| Configuration | Current Precipitation/Humidity widgets, original units and intervals, brightness 49%, Always-on and router configuration retained/restored |
| Irreversible security changes | No eFuse writes; Secure Boot and flash encryption unchanged |

Application SHA-256: `7f7a15c7796b7437598a92a483f0fa370b8a31b318146dfda39e907e203a0f49`.

Factory merged-image SHA-256: `8f64766774d73cc7ce8bd565dac5501f904a783453e268c45bf14977bdfa6e3f`.

Pre-update backup SHA-256: `a585b5a51e47b5e163ada91b5c878e56063c11def38567d567e362feb6b246a7`. Full backups and raw device captures remain private.

## Behavior and checks

| Check | Result and scope |
| --- | --- |
| Catalog research | 100 unique URL/field choices, 73 URL templates, 19 providers; every field has dated direct HTTP 200 evidence over normal verified TLS without authentication or redirects |
| Catalog consistency | 6,453 assertions; exact reviewed JSON matches embedded data and actual compiled application; firmware limits checked before build |
| Browser host | 1,485 exact embedded-JavaScript assertions; all presets in both forms, search, source guidance, draft preservation, custom edits, saved-source recognition and prior session/poll/deadline regressions |
| C++ widget host | 925 actual-source assertions; all presets in both slots through validator, HTTP widget handler and configuration; controlled platform/HTTPS stubs |
| HTTP response host | 17 send/header/close/failure assertions against actual source with SDK stubs |
| Actual LVGL host | All 14 pages; API Home/full detail, countdown-to-Focus switching, Browser reopen/scroll, Always-on, credentials, keyboard and monotonic timers pass |
| Native Safari | Paired 1.0.4, both full native dropdowns, case-insensitive search/counts, retained current choice, no-match/clear/Enter, autofill, provider links, custom edit attribution, Save and reload |
| Real representative ESP32 feeds | UK carbon level `high`, NOAA geomagnetic scale `0 G`, USGS M7+ monthly count `0 events`; current Precipitation/Humidity restored and refreshed successfully |
| API display visibility | SHA-256-checked actual Home and Your data frames independently match both configured labels, current scalar values and units; both latest refreshes HTTP 200 without errors |
| Display/settings | Authenticated HTTPS and UART confirm Always-on and current 49% backlight; verifier leaves Home displayed; native Safari tests restore both widget configurations |
| Flash readback | Both OTA-slot MD5 readbacks match the final 1.0.4 and public 1.0.3 images; active sequence 7 is CRC valid and accepted |
| Startup | Three consecutive healthy display/UI boots; one ROM boot each; no crash markers; lowest reported startup minimum heap 62,592 bytes |
| Native-browser heap | Lowest reported minimum heap observed during preset tests: 60,116 bytes |
| Public hygiene | Owner home paths absent from application/merged/ELF/map; factory storage gaps erased; explicit public allowlist excludes backups, raw logs/captures and authentication material |
| Licenses | 22 full upstream texts and font/notice provenance included; original source/UX rights retained |

Two earlier UART screenshot transfers were rejected for interrupted framing. The complete diagnostic repeat passed the unchanged framing and SHA-256 checks, then both independent regional OCR matches. Its wrapper saved raw data privately and returned the original bytes unchanged. No corrupted image was accepted; no check was relaxed; the interruption cause remains unestablished. Native Safari tests subsequently restored the same configured weather sources and verified fresh results and reload persistence.

[Catalog and Safari verification](API_CATALOG_VALIDATION.md) and [its structured conclusions](API_CATALOG_VALIDATION.json) distinguish live provider research, exhaustive offline form/backend tests and representative real ESP32 fetches. [Structured release conclusions](RELEASE_VALIDATION.json) retain installed-image and validation details without credentials or local network identity.

Historical reports for [1.0.0](RELEASE_VALIDATION_1.0.0.md), [1.0.1](RELEASE_VALIDATION_1.0.1.md), [1.0.2](RELEASE_VALIDATION_1.0.2.md) and [1.0.3](RELEASE_VALIDATION_1.0.3.md) preserve their original ten-boot, network/API, three-minute idle, timer/Browser and native Safari OTA evidence. The earlier [1.0.3 Browser/API report](BROWSER_API_VALIDATION.md) remains dated to that release.

## Public previews and limits

Public previews are offline host renders of actual LVGL source. Live screen images, local addresses, pairing material, certificates and sessions are excluded from source and release packages.

![Offline Home](../artifacts/ui-preview/home_offline.png)

All 100 fields were checked by desktop HTTPS research and exercised in both forms/backend slots offline. Live ESP32 fetches cover representative new sources and the restored weather readings; all 100 were not fetched on the ESP32. Device navigation uses UART with strict checked framebuffer/OCR; physical finger taps and optical brightness/color were not measured. Forced rollback, deliberate power/network interruption and prolonged burn-in were not performed in this run. Public providers can change or rate-limit their APIs. SHA-256 sums establish integrity and are not publisher signatures.
