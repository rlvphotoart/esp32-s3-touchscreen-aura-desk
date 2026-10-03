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
- Ready on the credential keyboard dispatches the expected connection action with copied input.
- UTF-8 inputs beyond the Wi-Fi byte limits are refused with visible feedback.
- Countdown uses monotonic LVGL ticks; advancing wall-clock data does not alter its duration. Start, pause, elapsed-time progression and preservation while paused were verified.
- Clang C++17 syntax checking with `-Wall -Wextra` passes against the downloaded LVGL headers.

## Device release verification

The final device release passed ten consecutive reboots, live router/time/API checks, authenticated HTTPS controls, a real custom JSON widget, browser OTA, and accepted-slot/image readback. Home, Weather and Tools were captured from the device with verified pixel SHA-256 hashes and inspected. See [RELEASE_VALIDATION.md](RELEASE_VALIDATION.md) for the recorded results and physical observations that remain outside software screenshot verification.

Host rendering does not establish physical display orientation, touch accuracy, brightness response, RGB tearing, router authentication, internet access, or API operation. Device build/flash/boot and network observations must be recorded separately by the hardware owner task. The browser screenshot fixture uses `192.0.2.1` and pairing code `000000`, which are test values rather than actual device credentials.

An initial device screenshot appeared shifted from one row onward. Read-only inspection identified a 78-byte Arduino Wi-Fi warning inserted into the raw UART image stream at byte 269797, accounting exactly for the 39-pixel shift in RGB565. Release firmware now suppresses interleaved diagnostic logging and the decoder verifies exact framing and the device's pixel hash. The final images passed these checks and contain no shifted rows.

## Representative screenshots

- `artifacts/ui-preview/welcome_offline.png`: first-run introduction.
- `artifacts/ui-preview/home_offline.png`: usable offline dashboard.
- `artifacts/ui-preview/home_fixture.png`: populated layout test.
- `artifacts/ui-preview/password_offline.png`: router credentials and keyboard.
- `artifacts/ui-preview/weather_fixture.png`: forecast, units, sunrise/sunset and attribution.
- `artifacts/ui-preview/api_widgets_offline.png`: unconfigured widget states.

UI ownership is limited to widget creation, presentation, navigation and monotonic timers. Network, persistence, TLS, API parsing, firmware updates and board initialization are provided by the application services. Snapshot updates do not reconstruct the active screen or discard typed input.
