# AURA Desk / Horizon interface verification

The interface is original LVGL v8 C++, designed for the confirmed 480 x 480 panel. Its visual language uses warm ivory, ink blue, cobalt actions, teal status, restrained rounded cards, and Montserrat typography. The touchscreen interface includes fourteen pages: Home, Weather, Tools, Settings, Network, Wi-Fi credentials, Location, About, Air quality, Reference rates, Timer, Welcome, Browser pairing, and API widgets.

The native host renderer compiles the actual `firmware/AuraDesk/ui.cpp` and the same downloaded LVGL sources/configuration used by the target. It does not substitute HTML or a separate design mockup. Run `python3 tools/render_ui.py` on this macOS workspace to regenerate screenshots in `artifacts/ui-preview`.

## Verified on the host

- All fourteen pages render at exactly 480 x 480 in RGB565 before PNG conversion.
- Offline pages show unavailable data and connection guidance rather than fabricated readings.
- Valid cached readings with an unavailable age are labelled `Saved data / age unavailable`, including after reboot before clock synchronization. `Waiting for first update` is reserved for absent data. This applies consistently to Home, Weather, Air quality, and API widgets.
- Fixture pages exercise populated data, unit text, long provider labels, forecast rows, and browser pairing layout. Fixture values are illustrative test data. They are isolated in `firmware/ui_preview/render.cpp`, outside the target sketch directory, and never compiled into firmware.
- Every page was visually inspected after disabling engineering performance overlays. Functional controls and keyboard remain on-screen. Settings and About intentionally scroll to additional content.
- The keyboard is positioned explicitly, supports letters/numbers/symbols, directs input to the selected field, and supports its Ready/Cancel events.
- Password characters are immediately masked; Show/Hide requires an explicit tap.
- Twenty snapshot updates preserve the existing SSID, password, keyboard and widget objects.
- The Settings display card presents brightness and the Always-on display switch together within the initial viewport. Disabled mode reads `Dims after 3 minutes of inactivity.`; enabled mode reads `Keeps your selected brightness.`. The switch has an expanded 48-pixel touch area, and additional Settings rows remain accessible by scrolling with the dock fixed on-screen.
- Always-on switching dispatches `SetAlwaysOn` with `1` and `0`. Repeated snapshots, browser-origin changes and returning to Settings synchronize the switch without duplicate commands or reconstructing the active widgets. Both display modes passed the actual LVGL host regression; see the [historical display report](RELEASE_VALIDATION_1.0.1.md).
- Ready on the credential keyboard dispatches the expected connection action with copied input.
- UTF-8 inputs beyond the Wi-Fi byte limits are refused with visible feedback.
- Countdown uses monotonic LVGL ticks; advancing wall-clock data does not alter its duration. Start, pause, elapsed-time progression and preservation while paused were verified.
- Clang C++17 syntax checking with `-Wall -Wextra` passes against the downloaded LVGL headers.

## Device release verification

The 1.0.0 device release passed ten consecutive reboots, live router/time/API checks, authenticated HTTPS controls, a real custom JSON widget, browser OTA, and accepted-slot/image readback. Home, Weather and Tools were captured from the device with verified pixel SHA-256 hashes and inspected. See [the 1.0.0 validation](RELEASE_VALIDATION_1.0.0.md) for those results. Version 1.0.1 adds the Always-on switch and has separate idle, backlight, persistence and OTA verification in [its historical report](RELEASE_VALIDATION_1.0.1.md). Current release results are in [RELEASE_VALIDATION.md](RELEASE_VALIDATION.md). Physical observations remain outside software screenshot verification.

Host rendering does not establish physical display orientation, touch accuracy, brightness response, RGB tearing, router authentication, internet access, or API operation. Device build/flash/boot and network observations must be recorded separately by the hardware owner task. The browser screenshot fixture uses `192.0.2.1` and pairing code `000000`, which are test values rather than actual device credentials.

An initial device screenshot appeared shifted from one row onward. Read-only inspection identified a 78-byte Arduino Wi-Fi warning inserted into the raw UART image stream at byte 269797, accounting exactly for the 39-pixel shift in RGB565. Release firmware now suppresses interleaved diagnostic logging and the decoder verifies exact framing and the device's pixel hash. The final images passed these checks and contain no shifted rows.

## Representative screenshots

- `artifacts/ui-preview/welcome_offline.png`: first-run introduction.
- `artifacts/ui-preview/home_offline.png`: usable offline dashboard.
- `artifacts/ui-preview/home_fixture.png`: populated layout test.
- `artifacts/ui-preview/password_offline.png`: router credentials and keyboard.
- `artifacts/ui-preview/weather_fixture.png`: forecast, units, sunrise/sunset and attribution.
- `artifacts/ui-preview/api_widgets_offline.png`: unconfigured widget states.
- `artifacts/ui-preview/settings_offline.png`: brightness and automatic dimming mode.
- `artifacts/ui-preview/settings_always_on_offline.png`: brightness and Always-on mode.

UI ownership is limited to widget creation, presentation, navigation and monotonic timers. Network, persistence, TLS, API parsing, firmware updates and board initialization are provided by the application services. Snapshot updates do not reconstruct the active screen or discard typed input.

## 1.0.2 timer and Browser navigation regression

Both user-reported failures were reproduced with actual LVGL pointer hit-testing before the fix. Regression tests now click 5-minute and 15-minute countdowns, return to Tools, open Focus, and select both 25-minute and 50-minute presets. They check elapsed/reset state, start/pause, and reopening an existing running Focus session. Countdown retains its own 5/15-minute controls.

The fixed Settings Browser shortcut is tested by pointer taps across five close/reopen cycles. Tests also reopen the scrolled Browser row, preserve Settings scroll, update the displayed address/code from snapshots, and verify the offline hint. All 14 pages and the earlier Always-on/credential/monotonic timer checks pass. Device-page reentry and real HTTPS pairing are recorded separately in the current release validation.

## 1.0.3 custom API Home and browser regression

Home has two 48-pixel API tiles above the dock for enabled widgets, or a Your data configuration shortcut when both are disabled. Pointer tests open each tile, confirm full values on the detail page and return to Home; the Settings API row returns to Settings. The existing weather, air, currency and timer cards remain accessible. Snapshot changes update the tile objects without rebuilding the active page.

Fresh and retained-reading fixtures verify genuine zero, long numeric Home compaction, full detail precision, fetching, clock/network prerequisites and independent two-line error messages. Retained Home values use an amber Saved label and an error indicator. These test fixtures remain outside the target sketch and public release previews.

The exact embedded browser JavaScript passes 56 offline DOM assertions for ready examples, form edits, validation feedback, expiry, wrong-code preservation, shared polling and bounded fetch/body deadlines. Actual C++ widgets pass 125 controlled assertions, and HTTP response policy passes 17 send/header/close assertions. Actual Safari/API and checked device Home/detail outcomes are documented in [BROWSER_API_VALIDATION.md](BROWSER_API_VALIDATION.md).

## 1.0.4 searchable public API catalog

Both Browser widget forms contain the complete 100-choice catalog in native dropdown category groups, with a separate labeled search field and an accessible match count. Every choice is exercised in both forms by the exact embedded-JavaScript regression. Selecting a preset only fills the form; Save applies it. The source hint and provider documentation update with the chosen reading.

Search is case-insensitive across names, providers, topics and labels. It preserves both the selected choice and draft fields, retains a filtered-out choice under Current selection, and restores all 100 choices when cleared. Enter cannot submit the form from the search field. Initial pairing/reload recognizes matching saved URL/field pairs without rewriting customized labels, units or intervals. Editing a URL/field clears the old provider association. Out-of-range saved coordinates reject a city preset without changing fields.

The reviewed catalog and embedded data are checked for exactly 100 unique URL/field pairs, direct HTTP 200 verification evidence, firmware byte limits and current generation. Actual C++ backend and HTTP-handler tests accept every expanded choice in both slots. [Catalog release verification](API_CATALOG_VALIDATION.md) records the final Safari and device observations separately.
