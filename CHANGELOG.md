# AURA Desk changes

## 1.0.7 — Automatic API endpoint and field completion

- Selecting a ready-to-use service immediately fills its matching or first installed reading, including the public HTTPS address and JSON field. Save remains explicit; Use is available to reapply the reading.
- Defaults both widgets to a Ready-to-use APIs only view. Turn it off to explore all 500 discovery services; manual setup and access requirements remain visible for entries without compatible readings.
- Adds a verified Meteo.lt Vilnius forecast temperature and a Jolpica F1 championship leader reading, bringing the total to 124 templates across 41 catalog services plus retained independent readings. Jolpica explicitly replaces the legacy F1 Data endpoint that returned HTTP 404.
- Preserves drafts during search/filter changes and manual/own API selection. Locks and restores picker state during Save to keep the selected service and submitted source consistent.
- Adds endpoint/field-specific autocomplete regressions in both slots and coverage for the ready filter, explicit Save, existing-source recognition and busy-state isolation. The API backend, touchscreen source, settings format, pairing and TLS implementation are unchanged.

## 1.0.6 — Explicit browser API selection and saving

- Adds **Use this API in widget 1/2** beside the public-service selector and a **Save widget 1/2** button beside the reading selector. Both Save buttons share the existing form submission path.
- Using a service with installed readings fills its selected matching template, or its first available template. Using a service without a reading starts a clean manual draft, including a label limited to 27 UTF-8 bytes, empty endpoint/field/unit, and a 30-minute interval.
- Shows which service owns the current draft. Browsing preserves edits; saving while browsing an unrelated service requires an explicit Use action, reading selection, or return to **All services / your own API**.
- Keeps service documentation separate from API configuration. Manual sources require a compatible public HTTPS JSON endpoint and scalar field; documentation links are never automatically copied into the endpoint. Services needing credentials or additional format support cannot be prepared unless a compatible reading is installed.
- Adds feedback near the selectors, guards empty enabled endpoint/field submissions, and disables all widget action buttons during a save while rejecting duplicate submissions.
- Adds exhaustive host regressions for all 500 services in both slots, template/manual selection, UTF-8 labels, source mismatch protection, independent widget drafts and the shared save/busy path. Device controls, data-fetching behavior, pairing and transport security are unchanged.

## Documentation refresh — 4 October 2026

- Refreshes the front page for the current 1.0.5 interface with a reviewed actual-device Home frame and current-source Your data, Always-on and 500-service companion previews.
- Adds screenshot provenance and linked GitHub Issues with symptoms, diagnosis, fixes, release commits and validation evidence.
- Marks the generated browser catalog include for correct GitHub language highlighting and exclusion from language statistics.
- Clarifies API discovery versus ready templates, pairing/setup and the on-device widget workflow. The verified 1.0.5 firmware release assets retain their original snapshots.

## 1.0.5 — 500-service browser companion

- Adds all 500 distinct reviewed API services across 50 topics to both browser widget selectors, with searchable groups, documentation, access evidence, formats and setup requirements.
- Separates service browsing from reading selection, preserving drafts and avoiding provider requests while browsing.
- Adds 22 bounded public JSON scalar profiles, bringing the reading selectors to 122 templates while retaining the original 100 choices. Thirty-nine catalog services have installed readings; 461 retain manual setup and compatibility guidance.
- Keeps the full catalog in flash-resident browser assets and adds generator freshness, exact embedded JavaScript, catalog evidence, license and production-backend checks.
- Verifies OTA settings preservation by comparing saved widgets, location, router and display configuration before and after the update.
- Rejects release packaging when final current-version device, browser or display evidence is incomplete, or report hashes disagree with the packaged firmware/catalog.
- Uses four standard ECDHE RSA/ECDSA AES-GCM cipher suites for verified public HTTPS requests, resolving GBIF's rejection of the SDK's broad cipher offer without changing trusted roots, hostname checks, groups or signatures.

## 1.0.4 — 100 public API presets

- Adds exactly 100 verified public HTTPS JSON URL-and-field presets from 19 providers in both Browser dropdowns, with 17 category groups and search.
- Presets fill valid labels, URLs, fields, units and refresh intervals; saved-city choices use the saved location. Each choice has provider documentation and source guidance.
- Search preserves selection and edits, Enter does not submit, matching saved sources are recognized, and custom URL/field edits clear stale preset attribution.
- Replaces the rate-limited CoinMarketCap dropdown example with Coinbase Bitcoin; preserves existing saved custom sources and the manual API option.
- Adds per-preset live verification records and exhaustive browser/C++ catalog checks, plus live Safari/device release evidence.

## 1.0.3 — Custom API readings on Home and Safari reliability

- Shows both enabled custom API readings directly on Home. Each tile opens Your data with full values, update ages and independent errors; returning goes back to the originating page.
- Adds ready-to-use public JSON API examples, array dot-path help, and feedback beside each Browser form.
- Reports per-widget fetching and request/JSON/field errors instead of indefinite waiting. A failed refresh retains the last successful reading with a clear warning.
- Makes configuration validation consistent across browser submission and persisted settings.
- Keeps pairing errors visible, prevents overlapping or indefinitely stalled browser polls, and closes completed HTTPS responses to release TLS connection resources.
- Adds actual Safari OTA/API tests, checked device Home/detail screenshots, and host custom-widget regression evidence.

## 1.0.2 — Timer and Browser navigation

- Tools → Open timer selects or resumes Focus, including after 5/15-minute countdowns. Focus 25/50-minute presets change the duration correctly. Countdown has separate 5/15-minute controls.
- Settings has a visible Browser button. Browser access can be closed/reopened repeatedly; returning preserves Settings scroll.
- Public maintenance tools read the expected device identity from runtime configuration. Local build paths are removed from release binaries/debug metadata; private data is excluded from Git and release packages.
- Adds public release documentation and dependency license texts.

## 1.0.1 — Always-on display

- Adds a saved Always-on display choice in touchscreen and browser Settings.
- On keeps selected brightness. Off retains three-minute inactivity dimming, one-fifth brightness with a 10% floor.
- Tests cover both persistence modes and actual idle/backlight transitions on the connected device.

## 1.0.0 — Initial AURA Desk release

- Original Horizon UI with 14 pages, router setup, clock, Open-Meteo weather/air quality, ECB reference rates, two public JSON widgets, Focus/countdown/stopwatch, brightness and local paired HTTPS OTA.
- Complete original external-flash backup and verified initial installation; dual 5 MiB slots with deferred startup health acceptance.
- Corrects the Arduino NetworkEvents startup race with consistent `NETWORK_EVENTS_MUTEX` and callback registration before Wi-Fi startup.
- Validates ten consecutive boots, live APIs, browser access/CSRF/export, custom widget data and OTA readback.

## Source-history provenance

The project had no Git commits before public publication. Version 1.0.0 source is recovered from the retained release archive. Version 1.0.1 firmware source is recovered from the target build's copied inputs and retained sketch files. These recovered snapshots are committed with current publication dates and privacy edits; historical commit dates are not fabricated. Version 1.0.2 records the timer/Browser fixes and public-release preparation. Private device backups, credentials and raw captures are retained outside public history.
