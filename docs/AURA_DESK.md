# AURA Desk 1.0.0

This source-history snapshot omits local firmware binaries, private recovery backups, and live device captures. Paths to those historical local artifacts are retained as documentation rather than public downloads.

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
| Home | Home in the bottom navigation | Clock, date, outside conditions, air quality, EUR/RON, and current timer |
| Weather | Weather navigation or Outside card | Temperature, feels-like, humidity, wind, three forecast days, sunrise and sunset |
| Air quality | Home → Air Quality | European AQI, category, PM2.5, source, and data age |
| Currency reference | Home → EUR/RON | EUR/RON and EUR/USD with ECB publication date |
| Tools | Tools navigation | Focus timer, 5-minute and 15-minute countdowns, and stopwatch |
| Timer | A timer button or Home timer card | Start, pause, resume, reset, and focus presets |
| Settings | Settings navigation | Network, location, brightness, browser access, API widgets, and diagnostics; scroll for lower rows |
| Network | Settings → Network or Home connection status | Nearby 2.4 GHz networks and manual entry |
| Wi-Fi credentials | Select a network or enter one manually | Network name, masked password, keyboard, and connection feedback |
| Location | Settings → Location | Online city lookup and saved location |
| Browser access | Settings → Browser configuration | Local HTTPS address and pairing code |
| Your data | Settings → API widgets | Two public API widget readings and their data ages |
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

Connect your phone or computer to the same router, pair the browser as described below, and scroll to **Your data, your way**. Each of the two widgets has an Enabled checkbox, display label, public HTTPS API address, JSON field path, optional unit, and refresh interval.

A dot path selects a value from a JSON response. For example, this illustrative response:

```json
{"current":{"temperature":21.5},"readings":[{"value":42}]}
```

supports `current.temperature` or `readings.0.value`. These are examples of the response format, not built-in sample readings.

Widgets accept a short text, number, or boolean. Choose a label up to 27 bytes, unit up to 15 bytes, URL up to 200 characters, field path up to 80 characters, and interval from 300 seconds to 86400 seconds. A longer returned value or a missing field is treated as an unsuccessful update; the last successful reading remains available during that powered session.

Use a public API that returns HTTP 200 JSON directly. API keys, authentication headers, account logins, private-network addresses, redirects, arbitrary scripts, and responses above 32 KiB are outside v1. The device verifies the remote HTTPS certificate through its bundled trusted roots. Save changes with the widget's **Save widget** button, then open **Settings → API widgets** to see the result. Disable a widget to stop its polling.

## Focus, countdown and stopwatch

Open **Tools** for a 25-minute or 50-minute focus session, a 5-minute or 15-minute countdown, or a stopwatch. Use **Start**, **Pause**, **Resume**, and **Reset** as appropriate. Countdown completion is shown visually. The Home timer card updates while you browse other pages.

One timer mode is active at a time. Selecting a different preset resets that session. Timers use monotonic elapsed ticks, so a network clock correction does not change their duration. A reboot or power loss ends the session; v1 does not resume timers automatically, schedule recurring alarms, play an audible alert, or run an automatic work/break sequence.

## Display settings

**Settings → Display brightness** adjusts the saved level from 10% to 100%. After three minutes without touchscreen interaction, the backlight dims to approximately one-fifth of that level with a 10% floor. Touch restores the selected brightness. The application stays active during dimming; the display is not entering deep sleep.

The v1 interface is English and uses metric weather units. Language selection, alternate units, and additional visual themes are not implemented.

## Local browser management

1. Put the phone or computer on the same router as the device.
2. Open **Settings → Browser configuration** on the touchscreen.
3. Enter the exact displayed `https://` address in your browser. The IP address may change after a router reconnect or reboot.
4. The device uses its own HTTPS certificate. A browser may require a certificate exception. Apply it only to the local device address displayed on your touchscreen.
5. Enter the six-digit code shown on **Browser access**, then choose **Pair this browser**.

The paired page provides status, brightness/location changes, router configuration, data refresh, settings export, widget configuration, and firmware updates. It connects directly to your device and needs no port forwarding. Changing router settings can close the browser connection; reopen the address now shown on the touchscreen.

The pairing code changes when the application restarts. Browser sessions are held in RAM, expire after inactivity or their maximum lifetime, and end on a reboot. Settings exports omit passwords, pairing codes and TLS private keys. Saved Wi-Fi credentials and the local TLS key remain on the device; the application does not make them part of an export or serial status output.

## Firmware updates and recovery

For a compatible AURA Desk update, pair the local browser, choose **Firmware update**, and upload the **application image**:

- AuraDesk.ino.bin (`../releases/aura-desk-1.0.0/AuraDesk.ino.bin`; historical local artifact omitted from public history): application image for browser OTA.
- AuraDesk.ino.merged.bin (`../releases/aura-desk-1.0.0/AuraDesk.ino.merged.bin`; historical local artifact omitted from public history): complete 16 MiB factory image for the serial installation/recovery tooling; not a browser OTA file.

The firmware has two 5 MiB application slots. An update writes to the inactive slot, verifies the image structure/integrity and ESP32-S3 target, selects it for the next boot, and restarts. Startup health checks defer acceptance until the new application is running. If a pending update fails those checks, the rollback mechanism can return to the previous valid custom application. It does not restore the vendor firmware or recover a changed partition layout.

Keep power connected during installation. Use application binaries from the matching AURA Desk release; image integrity validation is not a publisher-signature verification feature. Secure Boot, flash encryption and anti-rollback eFuses are not enabled or changed by this firmware installation.

The original 16 MiB firmware snapshot was acquired again before replacement and retained privately at:

- Original full flash (`../backups/pre-aura-20261003/full_flash_original.bin`; historical local artifact omitted from public history)
- Original backup manifest (`../backups/pre-aura-20261003/manifest.json`; historical local artifact omitted from public history)

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
