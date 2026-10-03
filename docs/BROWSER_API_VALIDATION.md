# AURA Desk 1.0.3 — Safari and custom API verification

This report distinguishes native Safari interactions, actual device framebuffer/HTTPS checks, and offline regression tests. Raw device addresses, pairing material, certificates, router details and captures remain private. Public conclusions are recorded in [BROWSER_API_VALIDATION.json](BROWSER_API_VALIDATION.json).

## Working public examples

| Example | Public HTTPS address | JSON field | Unit | Refresh |
| --- | --- | --- | --- | --- |
| Bitcoin price · CoinMarketCap preset | `https://pro-api.coinmarketcap.com/public-api/v2/simple/price?symbol=BTC&convert=USD` | `data.0.quotes.0.price` | USD | 1800 seconds |
| Bitcoin price · Coinbase alternative | `https://api.coinbase.com/v2/prices/BTC-USD/spot` | `data.amount` | USD | 1800 seconds |
| Humidity | `https://api.open-meteo.com/v1/forecast?latitude=<saved-latitude>&longitude=<saved-longitude>&current=relative_humidity_2m` | `current.relative_humidity_2m` | % | 1800 seconds |
| EUR/RON | `https://api.frankfurter.dev/v1/latest?base=EUR&symbols=RON` | `rates.RON` | RON | 21600 seconds |
| UK carbon intensity | `https://api.carbonintensity.org.uk/intensity` | `data.0.intensity.forecast` | gCO2/kWh | 1800 seconds |

Bitcoin and humidity were exercised end to end. The final device configuration uses Coinbase Bitcoin spot price because CoinMarketCap returned HTTP 429 after the validation reboots. The CoinMarketCap preset remains available. Coinbase documents its [public spot endpoint and scalar amount](https://docs.cdp.coinbase.com/coinbase-app/track-apis/prices). The other two are documented presets covered by configuration/form tests; this report does not claim they were fetched live in this release run.

CoinMarketCap documents a [keyless public API](https://coinmarketcap.com/api/documentation/pro-api-reference/keyless-public-api) and its V2 response shape. Its legacy V1 simple-price endpoint has a different shape: `data.0.price`. A URL alone is insufficient: enable the widget and supply the exact scalar field path. Public providers may rate-limit the shared network address; the device reports HTTP 429 and waits before retrying. [Open-Meteo documentation](https://open-meteo.com/en/docs) defines the current relative humidity field; the preset fills the saved city coordinates rather than guessing a location.

## Browser behavior

Native Safari was used for pairing, the ready-to-use Bitcoin/humidity forms, the manual Coinbase source, valid saves, malformed-path rejection, a missing-field response, manual refresh, reload/persistence, settings export and application OTA. The final release outcomes are in the structured report. An earlier private 1.0.3 candidate also exercised a real provider HTTP 429: the last successful Bitcoin value and its age stayed visible while humidity remained valid.

A malformed path such as `data.` is rejected beside the form. A syntactically valid but absent field is accepted as configuration, then shows a concrete field error after the API responds. These are distinct outcomes. A failed update keeps the last successful reading; changing a source clears the previous source's value. Fetching, rate limits, HTTPS failures, bad JSON and unavailable fields are reported independently for each widget.

The final page performs one initial session check, stops unpaired polling, retains the specific wrong-code message and shares a single in-flight status request. Fetch deadlines cover response-body reading and release timers in all paths. Completed HTTPS responses close their transport connections so that idle browser TLS buffers do not remain allocated while the device calls public APIs. This resource-policy change addresses observed intermittent HTTPS failures; an out-of-memory cause was not established by the private TLS diagnostic probe.

## Touchscreen behavior

Both enabled API widgets appear in separate 48-pixel Home tiles above the navigation dock. Tapping either opens **Your data**, with full values, data ages and concrete error messages. Home may compact a long numeric value; the detailed page retains its full precision. A retained reading is marked **Saved**. Genuine zero is a valid reading. With neither widget enabled, Home shows a **Your data · Configure your APIs** shortcut.

Back returns to the originating Home or Settings page. Actual LVGL pointer tests cover both entry routes, compact/full values, saved-value warnings, model updates and the disabled shortcut. The identity-checked device verifier reads SHA-256-framed Home and Your data screenshots, compares each card's own label/value/unit against authenticated status, and preserves display/widget settings. These device checks use UART page navigation; physical finger taps and optical panel quality were not measured.

## Offline regression scope

- 125 assertions exercise actual C++ widget validation, scalar extraction and request/error behavior with controlled platform/HTTPS stubs.
- 56 assertions exercise the exact embedded browser JavaScript and form/session/poll/deadline behavior in an offline DOM harness.
- 17 assertions exercise actual HTTP response headers, complete-send/close ordering and error propagation with SDK stubs.
- All 14 actual LVGL pages render; pointer regressions cover API Home/detail navigation plus the timer, Browser, display and credential flows.

The release does not add API-key/header authentication, redirects, image rendering, arbitrary objects/arrays as readings, or cloud forwarding. Custom feeds must return a supported scalar in public HTTPS JSON.
