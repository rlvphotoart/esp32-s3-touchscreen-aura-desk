# AURA Desk 1.0.1 — Always-on validation

Validated on the connected ESP32-S3 touchscreen on 2026-10-03. The update preserves configuration and adds a saved Always-on display switch to touchscreen Settings and local browser settings.

- Target compilation and all 14 actual LVGL host pages passed. Switch dispatch, snapshot synchronization, navigation and scrolling passed.
- Both Off and On persisted across separate healthy application restarts and authenticated settings exports. Strict JSON boolean validation passed.
- At 183,284 ms of actual touch inactivity, Always-on retained the selected 78% backlight driver level.
- Disabling it at 185,298 ms applied the original 15% dim level. Enabling it at 186,426 ms restored 78% without touch.
- Private HTTPS OTA installation passed. Readback confirmed ota_0, sequence 3, VALID, with the exact release application SHA-256. The previous 1.0.0 image remains VALID in ota_1.
- The final post-readback boot passed display/UI/startup health, router, clock and valid API status, with Always-on enabled at 78%. No crash markers were reported.

The full test completed both persistence phases; its initial idle window expired after touch activity reset the idle counter. The separate idle-only run completed the uninterrupted idle and backlight transition checks. The first connection attempt was inconclusive after a restart; later instrumented pairing and restarts passed.

Application SHA-256: `ce8ec24e04035c1e1c7d8de940e304656eb0fe5594f4b2989200b19acfa0c397`. Fresh pre-update 16 MiB backup SHA-256: `a150b4ca0fc1b6cfba889f955f8aef5f8c314ca040fd5c30e6500bd0441d4817`; complete device MD5 verified.

[Structured conclusions](RELEASE_VALIDATION_1.0.1.json). [Earlier 1.0.0 validation](RELEASE_VALIDATION_1.0.0.md) contains the earlier ten-boot and full API checks. Backlight values are driver diagnostics; optical luminance and manual touch accuracy were not measured.
