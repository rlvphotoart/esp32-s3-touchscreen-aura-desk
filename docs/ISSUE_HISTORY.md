# AURA Desk issue and improvement history

[Browse completed GitHub Issues](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues?q=is%3Aissue%20is%3Aclosed%20label%3Ahistory).

Issues #1–#9 were recorded retrospectively on **4 October 2026 (Europe/Bucharest)** from retained release evidence. The dates below refer to validation of the delivered fixes. Final 1.0.5 acceptance and publication occurred after midnight on 4 October locally; earlier release evidence is dated 3 October. Issue #10 records the documentation refresh, #11 the browser selection/Save fix, and #12 automatic field completion. Each linked issue contains the symptom, diagnosis, change, fixed-version source and acceptance checks.

| Issue | Problem or request | How it was resolved | Delivered in | Validated locally |
| --- | --- | --- | --- | --- |
| [#1](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/1) | Wi-Fi event registration race during startup | Register callbacks before Wi-Fi startup and enable the event mutex consistently. | 1.0.0 | 2026-10-03 |
| [#2](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/2) | Make inactivity dimming optional with a saved Always-on setting | Save an Always-on choice in both device and browser settings. | 1.0.1 | 2026-10-03 |
| [#3](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/3) | Open timer retained the previous 5/15-minute countdown instead of Focus | Enter or resume Focus explicitly; give Focus and Countdown separate duration controls. | 1.0.2 | 2026-10-03 |
| [#4](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/4) | Browser pairing screen was hard to reopen from Settings | Keep a visible Browser header shortcut and preserve Settings scroll. | 1.0.2 | 2026-10-03 |
| [#5](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/5) | Custom API values visible in the browser were missing from Home | Show both API tiles on Home and link them to full Your data readings. | 1.0.3 | 2026-10-03 |
| [#6](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/6) | Improve Safari pairing feedback and bounded HTTPS polling | Retain pairing feedback, share in-flight polls, bound reads and close completed HTTPS transports. | 1.0.3 | 2026-10-03 |
| [#7](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/7) | Replace the rate-limited CoinMarketCap dropdown example with Coinbase | Offer Coinbase with data.amount while retaining saved custom sources. | 1.0.4 | 2026-10-03 |
| [#8](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/8) | Expand Browser discovery to 500 services and keep browsing separate from saving | Add 500 services and 122 separate readings with search and setup guidance. | 1.0.5 | 2026-10-04 |
| [#9](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/9) | GBIF rejected the SDK’s broad TLS cipher offer | Offer four ECDHE AES-GCM suites while retaining certificate and hostname verification. | 1.0.5 | 2026-10-04 |
| [#10](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/10) | Outdated front page and missing issue history | Refresh the gallery/README and publish linked issue records with evidence. | Documentation | 2026-10-04 |
| [#11](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/11) | Browsing a public API did not offer a clear way to apply and save it | Add Use this API and a nearby Save to both widgets; prepare a template or clean manual draft and guard against saving an unrelated source. | 1.0.6 | 2026-10-04 |
| [#12](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/12) | Selected APIs did not autocomplete the address and JSON field | Automatically fill ready-service readings, default to a ready-only view, and add verified Meteo.lt/Jolpica defaults. | 1.0.7 | 2026-10-04 |

The [changelog](../CHANGELOG.md) records release contents. The [1.0.5 full baseline](RELEASE_VALIDATION.md), [API services validation](API_SERVICES_VALIDATION.md), [1.0.6 browser maintenance validation](BROWSER_SELECTION_FIX_1.0.6.md), and [1.0.7 autocomplete validation](BROWSER_AUTOCOMPLETE_1.0.7.md) separate native browser behavior, actual ESP32 requests/display frames and offline renderer/backend checks. Earlier reports remain dated to their own releases. Recovered 1.0.0/1.0.1 source snapshots retain their real publication provenance.

## Earlier failed checks

An earlier 1.0.5 iNaturalist request failed without an HTTP response, and a separate display-frame transfer was truncated. Their causes were not established. The final complete 22-profile run and strict frame repeat passed with unchanged acceptance checks. These attempts remain in the validation evidence; they are not described as root-cause repairs or currently reproduced product bugs.

## Scope of completion

The catalog contains 500 searchable services and 124 reading templates. Forty-one catalog services have 117 associated readings, with seven original choices available independently. The other 459 services provide discovery/custom-configuration guidance. The catalog issue records completion of that browser feature; it does not assert 500 working ESP32 integrations.

The GBIF repair keeps certificate and hostname verification enabled. Public servers must support at least one configured TLS 1.2 ECDHE AES-GCM suite. A provider's later quota, schema or availability change can require a new issue and new evidence.

Public history contains conclusions, source links and reviewed screenshots. Original saved device configuration, local network identity, full-flash backups, raw API bodies, credentials and pairing/session material remain private.

## Report a new problem

[Create an issue](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/issues/new) with firmware version, board model, reproducible steps, expected/actual behavior and non-sensitive error text. Include a public endpoint/field only when it contains no key, token or personal query data. Historical Issues are closed after their documented fixes were accepted.
