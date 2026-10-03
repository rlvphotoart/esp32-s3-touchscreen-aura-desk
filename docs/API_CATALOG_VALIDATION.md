# AURA Desk 1.0.4 — public API catalog verification

Validated on 2026-10-03. The installed and accepted 1.0.4 image provides **100 distinct public HTTPS URL-and-field presets from 19 providers**, organized into 17 categories in each of the two Browser widget dropdowns. There are 73 distinct URL templates; some providers supply several readings. The complete list and dated per-field evidence are in [PUBLIC_API_CATALOG.md](PUBLIC_API_CATALOG.md) and [PUBLIC_API_CATALOG.json](PUBLIC_API_CATALOG.json).

## Catalog and software checks

| Gate | Result and scope |
| --- | --- |
| Live public API research | All 100 fields returned non-null numbers or short strings in direct HTTP 200 JSON responses over normally verified HTTPS; no credentials or redirects. Related fields reuse a response. Saved-city probes use public example coordinates. |
| Firmware limits | All URL, label, unit, dot-path, refresh and response-size bounds pass; 70 number fields and 30 short-string fields. |
| Canonical/embedded consistency | Exact 100 unique IDs and URL/field pairs; generated Browser data matches the reviewed JSON. Build refuses stale generation. |
| Catalog checker | 6,453 assertions; its self-test rejects 52 invalid/drift cases and passes 5,398 assertions. |
| Browser JavaScript | 1,485 assertions on the exact embedded code; all 100 field mappings in both slots, search/filter retention, provider links, saved-source recognition, custom edits, coordinates and prior session/poll/deadline behavior. Offline DOM harness. |
| C++ widgets | 925 actual-source assertions; all 100 expanded choices pass validation, actual HTTP widget handler and configuration in both slots. Controlled platform/HTTPS stubs. |
| HTTP response policy | 17 actual-source assertions; complete send, headers, close and failure handling. SDK stubs. |
| LVGL | All 14 real pages and existing Home API, timer, Browser re-entry, display, credential and keyboard regressions pass on the host. |

## Native Safari and ESP32 checks

Safari paired with the installed 1.0.4 device. Both native dropdowns exposed all 100 options and 17 topic headings. Both unfiltered forms reported 100 presets from 19 providers. A mixed-case Coinbase search returned seven matches; NOAA returned six; USGS returned four. A no-match search reported zero without discarding fields. Filtered-out selections remained under Current selection, clearing search restored the catalog, and Enter in search did not submit the form.

Native selections filled the correct URL, field, label, unit, interval, source hint and provider link. Editing a saved NOAA field changed the dropdown to Your own API and removed its old attribution; that invalid draft was not saved. The ESP32 then fetched these representative new sources through native Safari Save actions:

| Preset | Slot | Observed successful reading |
| --- | ---: | --- |
| UK grid carbon level · NESO | 1 | `high` — short text |
| Geomagnetic storm · NOAA | 2 | `0 G` — a genuine zero |
| M7+ earthquakes / 30 days · USGS | 1 | `0 events` — a genuine zero |

The currently saved Precipitation and Humidity sources were restored with their original labels, units and 1,800-second intervals. Both then showed successful fresh readings. Reload kept the paired session, recognized both saved presets and restored source guidance. Both searches were left clear. Brightness 49%, Always-on and the router configuration were retained.

The read-only hardware verifier independently checked both label/value/unit regions on actual Home and Your data frames using strict framing, SHA-256 pixel hashes and private regional OCR. Both enabled widgets had latest HTTP 200 refreshes without errors. Device navigation left Home displayed. The verifier did not write settings, flash or eFuses. Native Safari preset tests temporarily changed widget configurations and restored them.

Two earlier UART captures were rejected for interrupted framing. A complete diagnostic repeat passed every original frame/hash check and both regional matches. Its wrapper recorded private raw bytes and returned them unchanged; no damaged capture was accepted and no check was relaxed. The cause of the interrupted transfers was not established. Raw frames, pairing material, local addresses and sessions stay private.

## Scope

Live desktop HTTPS evidence covers all 100 fields. Browser/C++ offline checks exercise every choice in both slots. Live ESP32 fetches cover the representative sources above and the two restored weather readings; this is not a claim that all 100 were fetched on the ESP32. Provider limits and changing feeds remain observable through per-widget errors and retained-value ages.

[Structured conclusions](API_CATALOG_VALIDATION.json) · [Installed image and release checks](RELEASE_VALIDATION.md). Physical finger taps, optical quality, forced rollback and prolonged burn-in were not measured in this run.
