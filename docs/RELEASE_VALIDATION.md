# AURA Desk 1.0.5 — release validation

**Status: passed. The final AURA Desk 1.0.5 application is installed and verified on the ESP32, with native Safari, live APIs, device-rendered Home/Your data frames and three healthy restarts accepted.**

The browser companion contains **500 searchable public API services across 50 topics** and **122 scalar reading templates**. Each service has provider documentation, access/authentication evidence, formats and device-support notes. Browsing preserves widget drafts and does not request the provider or save a configuration.

These counts describe different capabilities: 39 listed services have 115 associated reading profiles; 461 provide discovery and manual-configuration guidance. Seven original GitHub/TimeAPI.io readings remain independently available, giving 122 total profiles. A service entry does not establish that every provider endpoint works on the ESP32.

## Final build and preservation

| Item | Result |
| --- | --- |
| Application | 2,484,336 bytes; fits both 5 MiB application slots |
| Factory layout | Complete 16 MiB merged image; application at 0x20000; custom partition and image checks pass |
| Compiled service data | Exact 493,222-byte generated catalog payload found once in the final application |
| Build checks | Original and new generated catalogs checked before compilation; public owner-path audit passes |
| Pre-update backup | Complete 16 MiB snapshot with full-device MD5 verification; snapshot remains private |
| Final installation | Passed: certificate-pinned HTTPS application OTA, healthy restart and exact settings preservation |
| Active/previous slot verification | Passed: active ota_1 at 0x520000 is VALID; both application readbacks match expected images |
| Consecutive restarts | Passed: three healthy boots, one ROM boot each, zero crash markers; minimum startup heap 100,936 bytes |

Application SHA-256: `5b061127026773a052d2dcd42823ae4dd746d03163d747614cabcdc3c4527209`.

Factory merged-image SHA-256: `97fb19ca7269bafac6f9a96dd66354b7dfdbc72e2b836c38bd9307d91badf541`.

Pre-update backup SHA-256: `433da3b762dd44d0f27d88c79fc976132f0f92011888f3d693c1c1b51543cfa7`. Only its size, checksum and verification conclusion are published; full backups, raw device captures and identity material remain private.

## Completed software checks

| Check | Result and scope |
| --- | --- |
| Service catalog agreement | 25,521 evidence, source, link, runtime and license checks; exactly 500 distinct services |
| Service checker negative cases | 38 malformed source, evidence and link fixtures rejected |
| Additional C++ profiles | 220 actual-source assertions; all 22 new profiles through validation, HTTP widget handler and configuration in both slots |
| Original catalog | 6,453 assertions; all 100 preserved templates satisfy recorded evidence and firmware limits |
| Original checker self-tests | 5,398 assertions; 52 invalid catalog cases rejected |
| Exact browser JavaScript | 16,732 assertions; all 500 services and 122 readings in both forms, metadata, search, draft preservation and saved-source/session regressions |
| C++ widget host | 925 actual-source assertions using controlled platform/HTTPS stubs |
| HTTP response host | 17 actual-source send, header, close and failure assertions |
| HTTPS TLS policy host | 20 actual-source assertions for trusted-root attachment, cipher storage/order/failures, callback wiring and preserved verification/group/signature defaults |
| Package acceptance gates | 156 evidence assertions, including current reports; 152 incomplete, mismatched, ambiguous or private-report fixtures rejected; current reports must bind to packaged image and catalog hashes |
| Actual LVGL host | All 14 pages; Home/full API detail, true zero, timers, Browser re-entry, display, credentials and keyboard regressions |

The browser fixtures model native dropdown behavior: a selected reading and its service remain reachable under an unrelated search, and selecting a service never copies its documentation URL into the API endpoint. Every service exposes human-readable evidence and access/format notes. These software checks use controlled host fixtures; they do not prove live provider or physical display behavior.

## HTTPS compatibility change

The initial ESP32 pass fetched 21 of the 22 additional profiles successfully; GBIF failed before an HTTP response with a secure-connection error. The initial run remains recorded in [API services validation](API_SERVICES_VALIDATION.md). The final target build offers these TLS 1.2 suites:

- `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`
- `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
- `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`
- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`

Public API servers must support at least one of these four suites. TLS 1.3-only, legacy-CBC-only or otherwise incompatible servers are unsupported. The certificate bundle and hostname checks remain enabled, and SDK group and signature settings are retained. The host policy check covers source behavior and callback wiring; all 22 additional profiles, including GBIF, passed verified live requests on the final device image.

## Installed-image acceptance

| Gate | Verified evidence |
| --- | --- |
| Application OTA | Final application installed through paired, certificate-pinned HTTPS; healthy restart; router, location, both widgets, brightness and Always-on settings compared and retained; device TLS leaf preserved |
| New live profiles | All 22 additional profiles returned HTTP 200 with bounded scalars on the final image; minimum observed heap 35,492 bytes; saved widget settings restored |
| Native Safari | Both menus expose 500 services in 50 groups and 122 reading templates; search, metadata and draft preservation passed; representative new Save/fetch flows work in both slots; reload and original configuration recognition passed |
| Device display | Actual Home and Your data frames pass strict framing, dimensions and pixel SHA-256; independent regional checks confirm both configured labels, values and units, including representative new readings |
| Readback | ota_1 at 0x520000 accepted as VALID, sequence 10; installed final application bytes match; the other accepted application also matches its expected diagnostic image |
| Restart stability | Three consecutive healthy display/UI boots, one ROM boot each, zero crash markers; brightness 49% and Always-on enabled retained |
| Final user configuration | Exact original widget forms restored and recognized on native Safari reload; both restored sources' latest requests succeeded; device returned to Home |
| Public package | Explicit public allowlist, firmware source/build agreement, ZIP CRC and byte/hash verification; private backups/captures and authentication material excluded |

The other OTA slot contains an accepted interim 1.0.5 diagnostic build used during the TLS investigation. The pre-update 1.0.4 image remains preserved in the verified private full-flash backup and the historical public release.

An initial GBIF handshake failure, an earlier generic iNaturalist request failure and a truncated display-frame transfer are retained as failed attempts in [API services validation](API_SERVICES_VALIDATION.md). The final complete API run and strict frame repeat passed without weakening the acceptance checks. The iNaturalist failure's cause was not established; an incomplete frame was never accepted.

[Structured release conclusions](RELEASE_VALIDATION.json) retain build identifiers and verified gates. [Service/API verification](API_SERVICES_VALIDATION.md) separates discovery evidence, bounded profiles, actual device requests and earlier failures; [original catalog verification](API_CATALOG_VALIDATION.md) retains the dated 1.0.4 evidence. Public GitHub asset delivery is checked after upload against the local package; it is separate from installed-device acceptance.

## History, licenses and limits

Reports for [1.0.0](RELEASE_VALIDATION_1.0.0.md), [1.0.1](RELEASE_VALIDATION_1.0.1.md), [1.0.2](RELEASE_VALIDATION_1.0.2.md), [1.0.3](RELEASE_VALIDATION_1.0.3.md) and [1.0.4](RELEASE_VALIDATION_1.0.4.md) preserve their original acceptance evidence. The [1.0.3 Browser/API report](BROWSER_API_VALIDATION.md) also remains dated to its release.

The package retains 22 upstream dependency license texts, plus the two MIT notices for catalog discovery directories. Provider data and access keep their own terms; directory licenses do not license API data. Original application/UX rights remain recorded separately.

All 500 services are represented in the browser, with 461 still requiring endpoint selection, review or adapters. Directory no-key claims and documentation reachability do not establish current free access or device compatibility. The original 100-profile desktop evidence is dated to 1.0.4; all 100 have not been fetched on the final 1.0.5 ESP32 image. All 22 additional live checks cover slot 0, with representative new native Safari and device-frame coverage in both slots. Public providers may change responses, quotas, payload sizes and field paths.

Device frame checks use UART and independent region matching, rather than a camera photograph or manual physical touch test. Optical brightness/color, forced rollback, deliberate power/network interruption and prolonged burn-in are outside these release gates. SHA-256 checks establish integrity and are not publisher signatures. Private identifiers, owner paths, credentials, pairing/session material, saved configuration, current API values and raw provider bodies are excluded from this report and the public package.
