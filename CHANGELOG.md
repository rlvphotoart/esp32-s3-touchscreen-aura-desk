# AURA Desk changes

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
