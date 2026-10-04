# AURA Desk 1.0.7 API autocomplete verification

Maintenance validation dated **4 October 2026, Europe/Bucharest**. [Issue #12](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/12) tracks the owner’s screenshots and the correction. [Machine-readable report](BROWSER_AUTOCOMPLETE_1.0.7.json) records application/source hashes and separate acceptance gates.

## Reported behavior and correction

The 1.0.6 catalog exposed Meteo.lt and the legacy F1 Data entry without reading templates. Use started a manual form, leaving Public HTTPS API address and JSON field blank. The owner expected selecting an API to fill those fields.

Selecting a ready-to-use service now fills its matching or first compatible installed reading immediately: endpoint, field, label, unit and interval. No Use click is required. Review the fields and select **Save widget** to apply them. Use remains available to reapply a reading. Choosing a different ready service prepares its reading; Save remains explicit.

Both widgets default to **Ready-to-use APIs only**, listing 41 catalog services with installed readings. Turn off the filter to explore all 500 services. The 459 discovery entries without a reading show access/setup guidance and preserve the current draft; no data endpoint is inferred from their documentation link. Your own API selection, search, filter changes and status polling retain editable drafts. During Save, picker state is locked and restored if a programmatic change occurs.

## Verified defaults for the reported selections

| Service | Public HTTPS endpoint | JSON field | Reading |
| --- | --- | --- | --- |
| Meteo.lt API | `https://api.meteo.lt/v1/places/vilnius/forecasts/long-term` | `forecastTimestamps.0.airTemperature` | First hourly temperature in the latest Vilnius forecast, °C; label includes LHMT attribution; 10,800-second interval |
| F1 Data API · Jolpica | `https://api.jolpi.ca/ergast/f1/current/driverStandings.json?limit=1` | `MRData.StandingsTable.StandingsLists.0.DriverStandings.0.Driver.familyName` | First reported driver in current-season championship standings; 1,800-second interval |

Meteo.lt is an explicit Vilnius example rather than the saved device city, and the first forecast hour is not claimed to be an observed current temperature. [Provider documentation and attribution terms](https://api.meteo.lt/).

The original Jacobbrewer F1 Data documented endpoint returned HTTP 404. The catalog explicitly replaces that unavailable provider with Jolpica while preserving the stable service ID and old discovery/failure provenance. Jolpica is identified as a different provider; the current transport already supplies its required identifying User-Agent. Published standings are separate from live timing, and an empty season can have no scalar. [Jolpica standings documentation](https://github.com/jolpica/jolpica-f1/blob/main/docs/endpoints/driverStandings.md).

Both new defaults returned direct anonymous HTTPS 200 JSON on desktop with normal certificate verification and no redirects. Recorded response sizes were 21,918 and 709 bytes; both selected scalars fit the existing 47-byte limit. Exact response hashes and timestamped checks are in [the profiles](PUBLIC_API_SERVICE_READINGS.json). The total is now **124 readings**, including 117 associated with 41 catalog services and seven retained independent readings.

## Build and browser acceptance

| Check | Result |
| --- | --- |
| Exact embedded browser JavaScript | 29,633 assertions passed, including ready-only/all-service filtering, automatic field completion in both slots, explicit Save, own/custom draft retention, saved-source recognition and busy-state isolation |
| Service/evidence/source checks | 25,636 passed; 38 malformed evidence/link/mapping/source fixtures rejected |
| Production C++ profile path | 240 assertions passed using offline platform stubs for all 24 additional profiles |
| HTTP/TLS source policies | 17 response-policy and 20 TLS-policy assertions passed using offline SDK stubs |
| Pinned ESP32-S3 build | Passed; generated catalogs current; custom image layout and public artifact path audit passed |
| Independent review | Browser logic, profile limits and unchanged backend reviewed without blocking findings |
| Native Safari synthetic fixture | Selecting Meteo.lt in slot 1 and Jolpica in slot 2 filled the exact address/field without Use or manual input; nearby Save accepted both; reload recognized both saved sources; the full-catalog filter remained accessible |

The synthetic fixture serves the exact embedded page with synthetic status and performs no provider or device requests. It is separate from paired-device tests.

## Application and wireless delivery

Application: `AuraDesk.ino.bin`, **2,494,304 bytes**. SHA-256:

```text
4b0eee4d9d0de7c43d11f739b6b02e376dcc47559b2e79b9425c6f054ee93e41
```

The image has a valid ESP32-S3 target, checksum and digest, carries the AURA Desk 1.0.7 runtime identifier and fits the existing 5 MiB application slots. This release updates the browser page, generated catalog and version identifier. API backend, touchscreen source, pairing, settings schema and TLS policy are unchanged.

The existing native Safari firmware update form uploaded the validated application over Wi-Fi. After restart, the paired companion reported AURA Desk 1.0.7 and exposed the updated controls. No serial cable was used. A post-update export matched the original saved city, coordinates, timezone, brightness, Always-on choice and both widget configurations.

Live selection filled the Meteo.lt address/field in widget 1 and Jolpica address/field in widget 2 without clicking Use or entering those fields manually. An export before Save confirmed that selection had changed only drafts. Nearby Save accepted both configurations; the ESP32 returned **14.4 °C** and **Antonelli**, respectively, with successful-request feedback. These are readings observed during this check, rather than timeless provider values. The saved exports matched both profile configurations exactly, and Safari reload recognized both sources with their saved fields.

The original Nature observations and Humidity widgets were restored, both fetched successfully, and the final Safari reload recognized their saved sources. The final exported configuration matched the original exactly for every compared location/display/widget field. Browser fixture results, actual device communication and restoration are recorded as separate checks in the JSON report.

## Scope and privacy

This is an application maintenance release for an existing AURA Desk installation. The complete factory/first-installation image remains in [v1.0.5](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/releases/tag/v1.0.5). The separately dated [1.0.5 full hardware/API/display baseline](RELEASE_VALIDATION.md) remains intact.

This run does not repeat full-flash readback, forced-restart acceptance, every provider request or physical-display capture. Actual device Save/fetch communication and browser behavior are distinct from physical-display acceptance. Public reports contain conclusions, public sample endpoints and hashes. Original saved configuration, local identity, raw captures, credentials and pairing/session material remain private. Earlier release assets and tags are preserved.
