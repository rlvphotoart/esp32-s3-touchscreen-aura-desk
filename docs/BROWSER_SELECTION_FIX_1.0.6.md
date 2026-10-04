# AURA Desk 1.0.6 browser selection and Save verification

Validated **4 October 2026, Europe/Bucharest**, on the existing ESP32-S3 installation and native macOS Safari. [Issue #11](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/11) records the reported problem and resolution. [Machine-readable conclusions](BROWSER_SELECTION_FIX_1.0.6.json) include source and application hashes.

## Problem and resulting behavior

Choosing a catalog service displayed its documentation but left the previous widget source in the form. The connection between browsing, preparing a source and saving it was unclear.

Both widgets now provide **Use this API in widget 1/2** beside the service selector and **Save widget 1/2** beside the reading selector. Use fills a compatible installed reading template. A service without a template starts a clean manual draft with its label and blank endpoint/field/unit, so a previous source cannot carry over silently. Supply a compatible public HTTPS JSON endpoint and exact scalar field, then Save.

Browsing preserves drafts. Saving an unrelated, newly browsed service before applying it produces guidance instead of submitting the previous source. Selecting **All services / your own API** permits an intentional custom draft. Missing endpoint/field checks and shared busy handling prevent an empty enabled source or duplicate concurrent Save. Guidance appears near the selectors and at the bottom of each form.

The catalog remains **500 services and 122 reading templates**. Documentation links are not substituted as data endpoints. Services that require credentials or unsupported formats still need integration work; this update does not make every catalog entry runnable.

## Delivered application

Only the embedded browser HTML/JavaScript and the application version identifier changed in firmware source. The API backend, saved-settings format, touchscreen source, pairing and TLS implementation match the previous source baseline. The existing application OTA path installed the update over Wi-Fi without using a serial cable.

| Property | Verified result |
| --- | --- |
| Runtime version | AURA Desk 1.0.6 in paired Safari after restart |
| Application | `AuraDesk.ino.bin`, 2,489,168 bytes |
| SHA-256 | `f4fe4a101402fee4c4ce772141229f3c08d7c29ccae81b5156da81317ee925cb` |
| Image checks | ESP32-S3 target, valid checksum/digest, fits the existing 5 MiB application slots |
| Wireless installation | Native Safari upload reached verified/restarting feedback; user re-paired directly with the new device code |

This is an **application maintenance release**. The complete first-installation/factory image and separately dated hardware acceptance remain in [v1.0.5](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/releases/tag/v1.0.5). Upload the 1.0.6 application image through the paired companion's Firmware update form. Keep power connected and re-pair after restart.

## Acceptance checks

| Check | Result |
| --- | --- |
| Exact embedded browser regressions | 29,432 assertions passed, including all 500 service selections in both slots, template/manual setup, source mismatch guidance, draft retention, UTF-8 label bounds and shared Save handling |
| Pinned target build | Passed; public artifact path audit and generated catalog freshness passed |
| Existing build prerequisites | 6,453 catalog checks, 25,521 service/evidence checks and 20 production TLS source checks passed |
| HTTP response policy | 17 checks passed |
| Native Safari fixture | Both slots passed template/manual Use, nearby Save, mismatch rejection and reload recognition using the exact embedded page with synthetic status |
| Live template in widget 1 | Coinbase Bitcoin template filled `data.amount`; nearby Save accepted; the ESP32 returned a reading with successful-request feedback |
| Live manual API in widget 2 | isEven Use cleared the previous source; empty enabled Save was rejected; entering a public endpoint and `iseven` field saved successfully and the ESP32 returned a boolean reading |
| Live reload | Saved template/manual fields survived Safari reload; the manual source correctly reopened as your own API |
| Configuration preservation | Post-OTA export preserved the original city, coordinates, timezone, brightness, Always-on choice and both widget configurations |
| Restoration | Original Nature observations and Humidity widgets restored; both fetched successfully; final reload/export matched the original configuration exactly |
| Independent review | Browser implementation, regression coverage and maintenance documentation reviewed; incorrect factory download link corrected |

The manual test used the documented [isEven API](https://isevenapi.xyz/) public endpoint. Fixture results and actual device requests are separate checks. Saved catalog association for manual sources is temporary browser state; the endpoint, field, label, unit, interval and enable choice are persisted.

## Evidence boundaries

This run verifies the changed browser workflow, actual device Save/fetch communication, wireless installation and settings preservation. It does not repeat full-flash readback, three forced restarts, every provider request or device-rendered frame capture from the [1.0.5 baseline](RELEASE_VALIDATION.md). The touchscreen source and API backend did not change; no new physical-display claim is made for this run.

Public reports contain reviewed conclusions and source/artifact hashes. Original configuration exports, raw browser/device captures, local identity, credentials and pairing/session material remain private. Existing 1.0.5 release assets and tags are preserved.
