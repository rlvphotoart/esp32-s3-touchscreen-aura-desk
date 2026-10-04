# AURA Desk 1.0.7

AURA Desk turns the 480 × 480 touchscreen into an internet dashboard with weather, regional air quality, currency reference rates, your own public API readings, and focus tools. Its original Horizon interface uses an ivory canvas, ink-blue cards, cobalt actions, and large touch controls.

This manual describes the implemented v1 application. Device installation, boot, display, touch, network, and update observations are recorded separately by the installation task; this manual is not a claim that those checks have all passed.

## First use and router connection

1. Keep the device powered through its existing USB connection. On the welcome screen, tap **Connect Wi-Fi**.
2. Choose your router's **2.4 GHz** network. Tap **Refresh** to scan again, or **Enter network manually** for a hidden network.
3. Enter the network password on the touchscreen. Characters are masked; **Show** reveals them until you tap **Hide**. Tap the network-name or password field to direct the keyboard to that field.
4. Tap **Connect**. After the router accepts the connection, tap **Continue** to reach Home. Clock synchronization and API requests follow automatically.
5. Open **Settings → Location** to change the initial city. Bucharest is an editable default, not a detected location. Type the city name and tap **Save location** while internet access is available.

Wi-Fi configuration stays on the device and is reused after reboot. The application accepts network names up to 32 bytes and ordinary passwords of 8–63 characters; an empty password is allowed for an open network. Enterprise login, captive-portal login, and 5 GHz-only networks are outside v1. Guest-network client isolation may prevent your phone from reaching the local browser page even when the device itself has internet access.

**Explore offline** opens the dashboard and timers without a network. You can connect later through **Settings → Network**. Before the first successful network-time synchronization, the clock shows `--:--`.

The top-right Home status separates **Offline**, **Wi-Fi connected**, and **Online**. A router connection alone does not establish that an API request succeeded. Old readings remain visibly dated during an outage.

## Touchscreen pages

The bottom navigation contains **Home**, **Weather**, **Tools**, and **Settings**. The other pages open from their related cards or settings rows.

| Page | How to open it | What it contains |
| --- | --- | --- |
| Welcome | First use, before configuration | Connect Wi-Fi or Explore offline |
| Home | Home in the bottom navigation | Clock, date, outside conditions, air quality, EUR/RON, current timer and both enabled custom API readings |
| Weather | Weather navigation or Outside card | Temperature, feels-like, humidity, wind, three forecast days, sunrise and sunset |
| Air quality | Home → Air Quality | European AQI, category, PM2.5, source, and data age |
| Currency reference | Home → EUR/RON | EUR/RON and EUR/USD with ECB publication date |
| Tools | Tools navigation | Focus timer, 5-minute and 15-minute countdowns, and stopwatch |
| Timer | A timer button or Home timer card | Start, pause, resume, reset, and focus presets |
| Settings | Settings navigation | Network, location, brightness, Always-on display, browser access, API widgets, and diagnostics; scroll for lower rows |
| Network | Settings → Network or Home connection status | Nearby 2.4 GHz networks and manual entry |
| Wi-Fi credentials | Select a network or enter one manually | Network name, masked password, keyboard, and connection feedback |
| Location | Settings → Location | Online city lookup and saved location |
| Browser access | Settings → Browser button in the header, or Browser configuration row | Local HTTPS address and pairing code |
| Your data | Home → either API tile or Your data shortcut; Settings → API widgets | Two public API widget readings, full values, data ages and errors |
| About AURA | Settings → About & diagnostics | Firmware, uptime, memory, connection, reset reason, data sources, restart, and Forget Wi-Fi |

Tap the back arrow to return from a detailed page. Settings and About intentionally scroll. Home cards provide direct access to their related detailed pages.

## Data and time

| Function | Source and meaning | Normal request interval |
| --- | --- | --- |
| Clock and calendar | Network time; starts with Europe/Bucharest and its daylight-saving rules | Automatic synchronization |
| Weather | Open-Meteo regional forecast/model values; temperature, feels-like, humidity, wind and rain probability | 30 minutes |
| Sunrise and sunset | Daily weather response for the saved location | Included with weather |
| Air quality | Open-Meteo / CAMS regional model; European AQI and PM2.5 | 1 hour |
| Currency | ECB dated reference rates, expressed as 1 EUR in RON/USD | 6 hours |
| API widgets | Your selected public JSON fields | Your chosen interval, 300–86400 seconds |

Failed requests retry with a delay; they do not replace valid readings with invented zeros or demonstration values. Data age is displayed on the device. Weather and air-quality snapshots are cached locally, with writes limited to roughly one per hour when updates succeed. Cache writes are not a guarantee that the most recent update will survive an immediate power loss. Custom widget configurations persist; their fetched readings are kept in RAM and fetched again after restart.

Weather and air quality represent regional models rather than sensors fitted to this device or guaranteed measurements at your desk. Currency values are published reference rates, not executable trading or card-conversion quotes. On weekends or holidays, the latest ECB publication can be older than the device's last successful request. Use its displayed publication date.

After a successful synchronization, the wall clock continues while the device remains powered, even if the network disconnects. A complete power loss requires network synchronization again: no battery-backed clock has been established. The firmware implements daylight-saving rules for listed common regions and explicitly uses UTC for an unsupported region; it does not claim a complete international timezone database.

Open-Meteo's hosted free access is intended for personal, non-commercial use. Provider availability, free-tier terms, and limits belong to each service. Sources and attribution appear in About and in the browser interface. [Open-Meteo Weather API](https://open-meteo.com/en/docs), [Air Quality API](https://open-meteo.com/en/docs/air-quality-api), [Open-Meteo usage terms](https://open-meteo.com/en/pricing), [ECB reference rates](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html)

## Your own API widgets

Connect your phone or computer to the same router, pair the browser as described below, and scroll to **Your data, your way**. Each widget has public-service and reading selectors, an Enabled checkbox, display label, public HTTPS API address, JSON field path, optional unit, and refresh interval. The same API can be used in either slot, or configure your own public JSON source.

1. Search by service, provider or topic and select a service under **Browse public APIs**. The default **Ready-to-use APIs only** view offers installed readings. Selecting one fills its public HTTPS address, JSON field, label, unit and interval immediately, while showing provider details.
2. Review the matching or first available reading. Choose another reading from its selector when needed. **Use this API in widget 1/2** is an optional way to reapply it; selecting the service already fills the fields.
3. Turn off **Ready-to-use APIs only** to explore all 500 entries. Selecting a discovery entry without an installed reading preserves your draft. For a compatible manual service, Use starts a clean form: its name becomes the label, endpoint/field/unit are empty, Enabled is checked, and the interval is 1800 seconds. Enter a verified public HTTPS JSON endpoint and exact scalar field path. The documentation link provides guidance; it is not used as the data endpoint.
4. Review the fields, then choose **Save widget 1/2** beside the reading selector or at the bottom of the card. Both buttons save the same form. An enabled widget needs an endpoint and field path before it can be saved. The device then requests the configured API and reports its result at the top of that widget card.

The draft status identifies the source you have prepared. If you select an unrelated discovery entry without applying it, Save requires Use, a reading choice, or a return to **Your own API / all readings** to save the current draft. This prevents saving a previous provider accidentally. Manually editing a prepared source remains supported. Search and filter changes retain drafts. Save feedback appears near the selectors and at the bottom; actions and picker controls are disabled during Save.

A dot path selects a value from a JSON response. For example, this illustrative response:

```json
{"current":{"temperature":21.5},"readings":[{"value":42}]}
```

supports `current.temperature` or `readings.0.value`. These are examples of the response format, not built-in sample readings.

Widgets accept a short text, number, or boolean. Choose a label up to 27 bytes, unit up to 15 bytes, URL up to 200 characters, field path up to 80 characters, and interval from 300 seconds to 86400 seconds. A longer returned value or a missing field is treated as an unsuccessful update; the last successful reading remains available during that powered session.

Use a public API that returns HTTP 200 JSON directly. API keys, authentication headers, account logins, private-network addresses, redirects, arbitrary scripts, and responses above 32 KiB are outside v1. The device verifies the remote HTTPS certificate through its bundled trusted roots. Save changes with the widget's **Save widget** button, then see the result in the two tiles on **Home**. Tap either tile for **Your data**, or open **Settings → API widgets**. Disable a widget to stop its polling. The browser shows fetching and concrete request/JSON/field errors beside the affected widget. A failed refresh keeps the last successful value and its age, with a warning. **Refresh data** requests a new update without waiting for the normal interval. A disabled widget retains its configuration but does not request data.

Home compacts long numeric readings to fit the tiles; **Your data** shows their full values. Failed refreshes mark retained values as **Saved** and show the error in the detail page. Back returns to the page you used to open Your data. When neither widget is enabled, Home shows a **Your data · Configure your APIs** shortcut.

Each widget has a **500-service catalog** across 50 topics and a separate **reading selector with 124 templates**. Search by name, provider or topic. The default **Ready-to-use APIs only** view lists 41 services with installed readings. Selecting one immediately fills its compatible public HTTPS address, JSON field, label, unit and refresh interval. Save remains a separate action. Turn off the filter to explore all 500 services, including 459 discovery entries needing manual setup.

Choosing a reading fills the form and selects its associated catalog service where one exists; **Save widget** applies it. **Use this API** reapplies a ready service's matching reading or its first reading. Clear the service selection with **Your own API / all readings** to browse every reading, including legacy choices outside the service catalog, or to save your current custom draft. Search, filter changes and selecting a discovery entry preserve edits. Selecting a ready service prepares its reading without requesting data until Save. Custom URL/field changes remove stale reading attribution while preserving the prepared service association. Service documentation and the reading's documentation are displayed separately.

The [500-service catalog](PUBLIC_API_SERVICES.md) records access evidence and integration requirements. The [24 additional readings](PUBLIC_API_SERVICE_READINGS.md) and [original 100 templates](PUBLIC_API_CATALOG.md) record exact URLs, fields and dated checks. Provider documentation was reviewed for 127 services; 373 remain directory discoveries with access and usage terms needing confirmation. Listing a service does not imply an installed adapter or guarantee current availability. A discovery entry without a reading needs manual setup and confirmation that its endpoint returns a supported scalar within device limits. **Use this API** remains unavailable for services needing API keys/account credentials or additional format support unless a compatible reading exists. Images, audio, XML, keyed services and large responses require additional support.

The 1.0.7 defaults include Meteo.lt's **Vilnius forecast temperature**, which reads the first hourly temperature in the latest published forecast, and Jolpica's **F1 championship leader**. Vilnius is an explicit public example rather than the saved device city. Jolpica explicitly replaces the unavailable legacy Jacobbrewer F1 Data endpoint; the catalog shows the replacement provider and documentation. [Autocomplete verification](BROWSER_AUTOCOMPLETE_1.0.7.md)

Numbers including zero are supported. Array indices start at zero: `data.0.price` selects the first price in a `data` array. Select a scalar field, not the entire object or array. Text/boolean values are supported; image URLs are displayed only as text, and image-only endpoints cannot be used as numeric/text JSON widgets. The [earlier Browser/API verification report](BROWSER_API_VALIDATION.md) records dated endpoint and behavior checks; it does not establish current availability for every catalog service.

## Focus, countdown and stopwatch

Open **Tools** for a 25-minute or 50-minute focus session, a 5-minute or 15-minute countdown, or a stopwatch. Use **Start**, **Pause**, **Resume**, and **Reset** as appropriate. Countdown completion is shown visually. The Home timer card updates while you browse other pages.

One timer mode is active at a time. Selecting a different preset resets that session. Timers use monotonic elapsed ticks, so a network clock correction does not change their duration. A reboot or power loss ends the session; v1 does not resume timers automatically, schedule recurring alarms, play an audible alert, or run an automatic work/break sequence.

## Display settings

**Settings → Display brightness** adjusts the saved level from 10% to 100%. The **Always-on display** switch directly below it controls automatic dimming. When enabled, the screen keeps your selected brightness continuously. When disabled, three minutes without touchscreen interaction dims the backlight to approximately one-fifth of that level, with a 10% floor; touch restores the selected brightness. Both brightness and the always-on choice are saved across restarts. Existing configurations default to automatic dimming until you choose otherwise. The same switch is available in the local browser under **Make it yours**. The application stays active in either mode.

The v1 interface is English and uses metric weather units. Language selection, alternate units, and additional visual themes are not implemented.

## Local browser management

1. Put the phone or computer on the same router as the device.
2. Open **Settings → Browser** using the button in the header, or scroll to **Browser configuration** on the touchscreen.
3. Enter the exact displayed `https://` address in your browser. The IP address may change after a router reconnect or reboot.
4. The device uses its own HTTPS certificate. A browser may require a certificate exception. Apply it only to the local device address displayed on your touchscreen.
5. Enter the six-digit code shown on **Browser access**, then choose **Pair this browser**.

The paired page provides status, brightness/location changes, router configuration, data refresh, settings export, widget configuration, and firmware updates. It connects directly to your device and needs no port forwarding. Changing router settings can close the browser connection; reopen the address now shown on the touchscreen.

The pairing code changes when the application restarts. Browser sessions are held in RAM, expire after inactivity or their maximum lifetime, and end on a reboot. Settings exports omit passwords, pairing codes and TLS private keys. Saved Wi-Fi credentials and the local TLS key remain on the device; the application does not make them part of an export or serial status output.

## Firmware updates and recovery

For a compatible AURA Desk update, pair the local browser, choose **Firmware update**, and upload the **application image**:

- [AuraDesk.ino.bin](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/releases/download/v1.0.7/AuraDesk.ino.bin): application image for browser OTA.
- [AuraDesk.ino.merged.bin · 1.0.5 baseline](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/releases/download/v1.0.5/AuraDesk.ino.merged.bin): complete 16 MiB factory image for the serial installation/recovery tooling; not a browser OTA file. Release 1.0.7 supplies an application update for an existing AURA Desk installation.

The firmware has two 5 MiB application slots. An update writes to the inactive slot, verifies the image structure/integrity and ESP32-S3 target, selects it for the next boot, and restarts. Startup health checks defer acceptance until the new application is running. If a pending update fails those checks, the rollback mechanism can return to the previous valid custom application. It does not restore the vendor firmware or recover a changed partition layout.

Keep power connected during installation. Use application binaries from the matching AURA Desk release; image integrity validation is not a publisher-signature verification feature. Secure Boot, flash encryption and anti-rollback eFuses are not enabled or changed by this firmware installation.

The original 16 MiB firmware snapshot was acquired again before replacement and retained privately at:

- Original full flash: retained privately by the owner.
- Original backup manifest: retained privately by the owner.

Its SHA-256 is:

```text
18d2f07ee3d3d216ed9a1b2b83accc40d5c925cd2902f9390a8f671c0ca3a1da
```

Restoring that snapshot is a complete serial recovery operation, including the original partition layout and saved settings. See [recovery procedures](RECOVERY.md), [backup evidence](BACKUP.md), and [the custom build/flash-layout requirements](FIRMWARE_BUILD.md). Never use ordinary Arduino CLI upload for this layout; its default offsets differ from AURA Desk's validated factory image.

## Diagnostics

Open **Settings → About & diagnostics** for uptime, reset reason, heap information, PSRAM, signal level, and source timestamps. **Restart device** restarts the application. **Forget Wi-Fi** removes the saved router credentials and opens network setup; it does not erase the entire firmware.

The known USB-UART connection provides a 115200 baud serial console. Commands include:

| Command | Result |
| --- | --- |
| `help` | Supported command list |
| `info`, `status`, `heap`, `uptime`, `version` | Compact firmware and runtime status |
| `wifi-scan` | Start a nearby-network scan |
| `refresh` | Request data updates |
| `screenshot` | Software-rendered screen in framed RGB565 binary format |
| `screen:<page>` | Engineering navigation to a numbered UI page |
| `reboot:confirm` | Explicit restart |

The screenshot output is binary data intended for the capture tooling, not ordinary terminal text. A software screenshot can establish rendering/layout; physical orientation, panel colours, touch behaviour, router authentication, HTTPS API operation, and OTA recovery still require their separate device checks.

## Platform and implementation limits

The target is the firmware-identified Jingcai/Guition ESP32-4848S040C_I_Y_3 profile: ESP32-S3, 16 MiB flash, 8 MiB OPI PSRAM, ST7701 RGB display, and GT911 touch. It uses Arduino-ESP32 3.1.1 with its matching official high-performance SDK, ESP32_Display_Panel, and LVGL 8.4.0. The exact dependency hashes and commits are in [TOOLCHAIN_LOCK.json](TOOLCHAIN_LOCK.json).

The original Horizon UX and application services are custom source. The platform, drivers, JSON library, and LVGL retain their upstream open-source licenses.

No external sensors or GPIO accessories are required. V1 does not implement BLE integrations, smart-home control, computer monitoring, native USB device functions, multilingual UI, commercial API accounts, cloud synchronization, recurring reminders, or public-internet hosting. Those features should not be inferred from silicon capabilities or earlier proposals. Native USB pins are occupied by this board's display/touch wiring; keep the known USB-UART path for diagnostics and recovery.

## Timer and Browser navigation in 1.0.2

**Tools → Open timer** opens Focus. It resumes an existing Focus session; arriving from Countdown or Stopwatch selects a fresh 25-minute Focus session. Tap **25 min** or **50 min** to select the desired Focus duration, then **Start**. The Countdown page has its own **5 min** and **15 min** presets. Selecting a preset resets elapsed time and pauses until Start.

The **Browser** button remains visible in the Settings header without scrolling. It opens the current local HTTPS address and pairing code. Closing and reopening Browser access works repeatedly. The Browser configuration row also remains available lower in Settings, and returning from detailed pages preserves your Settings scroll position. Pairing codes refresh after a device restart.
