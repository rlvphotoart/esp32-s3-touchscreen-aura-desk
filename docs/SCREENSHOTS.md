# Screenshots — AURA Desk 1.0.5

The front-page gallery was refreshed on **4 October 2026 (Europe/Bucharest)**. All four images show the current 1.0.5 interface and are published as an explicit, reviewed set.

## Device frame

`device-home-api.png` is an unedited 480 × 480 frame from the actual ESP32 during final 1.0.5 verification. It shows the public PubChem caffeine mass and Rick and Morty character readings used for the test, before the owner's original widgets were restored. The frame passed protocol boundaries, dimensions and pixel SHA-256 checks, followed by independent regional label/value/unit matching. It is a framebuffer capture, not an optical photograph of the panel.

Original saved widget configuration, network addresses, pairing codes and authentication material are absent. This Home frame is the specifically reviewed public exception; other live captures and raw logs remain private.

## Current-source previews

`preview-your-data.png` and `preview-settings-always-on.png` render the unchanged 1.0.5 `ui.cpp` through actual LVGL 8.4.0 on the host. Public fixture readings are **Caffeine mass 194.19 g/mol** and **Character Rick Sanchez**. Settings use a demo network/city, brightness 49% and Always-on enabled. These are screenshots of the actual UI renderer with deterministic data.

`browser-companion.png` is a Chromium screenshot of the exact HTML embedded by `web_service.cpp` and `api_services.js.inc`. It shows both 500-service selectors and both 122-reading selectors. A local read-only fixture supplies status data; writes are rejected and no provider/device requests occur. This preview is separate from the native Safari and real ESP32 tests in the release reports.

## Source and integrity

The code is preserved in [source tag v1.0.5](https://github.com/rlvphotoart/esp32-s3-touchscreen-aura-desk/tree/v1.0.5). These SHA-256 values bind the gallery to that release's sources:

- `firmware/AuraDesk/ui.cpp`: `ad2e7ca8a03e631d14f0bc110b5a82c9cd7cf2dc65323e848514ea80c34d3009`
- `firmware/AuraDesk/web_service.cpp`: `6879515a93e5499200dd46975fe27535b924d9f3d8c4c56d49741868501710b1`
- `firmware/AuraDesk/api_services.js.inc`: `3572ef46ff02c8334780963aebfaea91a871c263479d5439e9d409b56e8cb1a5`

| Image | Provenance | Pixels | PNG SHA-256 |
| --- | --- | --- | --- |
| [device-home-api.png](../artifacts/readme-1.0.5/device-home-api.png) | Actual final ESP32-rendered Home frame | 480 × 480 | `816c18cba5cbf055a96b87e02a83e07e135f0e768e5aa19d30cc1fa9f95fcce1` |
| [preview-your-data.png](../artifacts/readme-1.0.5/preview-your-data.png) | Current LVGL host preview with public fixtures | 480 × 480 | `461e12a9b63f44a24599f09ce69282a0659cc1c897cb08fc84092ff0129eb95a` |
| [preview-settings-always-on.png](../artifacts/readme-1.0.5/preview-settings-always-on.png) | Current LVGL host preview with demo settings | 480 × 480 | `6b775e2be2f695d94ec08cf90f6dd17c035f834672ce1b74c38c8f309fd85a3a` |
| [browser-companion.png](../artifacts/readme-1.0.5/browser-companion.png) | Exact embedded browser UI with demo status | 1040 × 1516 | `60e36d9731ad623ad3cedea01e647b7de28ebc76c5955b6c4c705a27c1bd9457` |

Historical offline images under `artifacts/ui-preview/` remain available for older dated reports. The current README uses the gallery above. Only these four new PNG paths are allowlisted for Git/public packaging; additional fixture images and private captures stay ignored.
