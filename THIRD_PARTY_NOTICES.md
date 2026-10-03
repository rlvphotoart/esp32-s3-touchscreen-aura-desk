# Third-party components

The original AURA Desk application and Horizon interface have the status recorded in [ORIGINAL_CODE_RIGHTS.md](ORIGINAL_CODE_RIGHTS.md). Upstream components and reused files keep their own licenses. Full license texts and copyright notices are supplied in [third_party/licenses](third_party/licenses), with byte hashes and sources in [PROVENANCE.json](third_party/licenses/PROVENANCE.json).

| Component | Verified version / source | License and included notice |
| --- | --- | --- |
| Arduino-ESP32 core and framework libraries | 3.1.1; source headers retain their individual notices | [LGPL-2.1-or-later](third_party/licenses/LGPL-2.1.txt), with component-specific notices |
| ESP-IDF SDK and Espressif display, expander, utility libraries | SDK commit `cfea4f7c9894526553c11f42f80c4d894aade2a7`; driver pins in the dependency lock | [Apache-2.0](third_party/licenses/Apache-2.0.txt), with component-specific notices below |
| Reused Espressif LVGL port | `lvgl_v8_port.cpp` and `lvgl_v8_port.h`; pinned display-library example; copyright 2024–2025 Espressif Systems (Shanghai) CO LTD | [CC0-1.0](third_party/licenses/CC0-1.0.txt); original SPDX headers retained |
| LVGL | 8.4.0, commit `4495f428630cc1741bd8bfd977f080e8460e8e8d` | [MIT, copyright LVGL Kft](third_party/licenses/LVGL-MIT.txt) |
| Montserrat font glyphs | Actual LVGL input font reports **Version 7.200**; copyright 2011 The Montserrat Project Authors | [SIL OFL 1.1, versioned Montserrat notice](third_party/licenses/Montserrat-7.200-OFL.txt) |
| Font Awesome font glyphs | LVGL's combined font input reports **Font Awesome 5.9.0**; copyright Font Awesome | [Upstream 5.9.0 notice](third_party/licenses/FontAwesome-5.9.0-LICENSE.txt) and full [SIL OFL 1.1](third_party/licenses/SIL-OFL-1.1.txt) |
| ArduinoJson | 7.4.2; copyright Benoit Blanchon | [MIT](third_party/licenses/ArduinoJson-MIT.txt) |
| Mbed TLS | SDK headers report 3.6.2; SDK-fork and upstream license files match byte for byte | [Apache-2.0 OR GPL-2.0-or-later, complete upstream license](third_party/licenses/mbedTLS-3.6.2-LICENSE.txt) |
| esptool maintenance dependency | 5.4.0; host dependency, separate from the target application | [GPL-2.0-or-later](third_party/licenses/GPL-2.0.txt) |
| Vendored partition-table utility | ESP-IDF v6.1; exact source/hash in `tools/vendor/PROVENANCE.json` | [Apache-2.0](third_party/licenses/Apache-2.0.txt); original SPDX header retained |

Additional SDK/runtime component notices are retained separately:

| Component | Included upstream notice |
| --- | --- |
| Espressif Wi-Fi and PHY binary libraries | [Espressif binary redistribution terms](third_party/licenses/Espressif-radio-binaries-LICENSE.txt), from the exact SDK submodule commits |
| FreeRTOS kernel | [MIT notice](third_party/licenses/FreeRTOS-MIT.txt), from the pinned IDF commit |
| lwIP | [COPYING](third_party/licenses/lwIP-COPYING.txt), from the pinned IDF submodule commit |
| HTTP parser | [MIT notice](third_party/licenses/http-parser-MIT.txt), from the pinned IDF commit |
| WPA supplicant | [COPYING](third_party/licenses/WPA-supplicant-COPYING.txt), from the pinned IDF commit |
| cJSON | [MIT notice](third_party/licenses/cJSON-MIT.txt), from the pinned IDF submodule commit |
| esp_littlefs wrapper | 1.16.1, confirmed in the high-performance SDK dependency lock and header; [MIT notice](third_party/licenses/esp-littlefs-MIT.txt) |
| LittleFS | [BSD-3-Clause notice](third_party/licenses/littlefs-BSD-3-Clause.txt), from the wrapper's exact LittleFS submodule commit |
| Newlib | [IDF notice collection](third_party/licenses/IDF-newlib-COPYING.txt) and [installed toolchain notice collection](third_party/licenses/toolchain-newlib-COPYING.txt) |
| GCC runtime libraries | [GPL 3 text](third_party/licenses/GCC-GPL-3.0.txt) and [GCC Runtime Library Exception 3.1](third_party/licenses/GCC-Runtime-Exception-3.1.txt), copied from the installed toolchain |

The font lineage is recorded in [FONT_PROVENANCE.json](third_party/licenses/FONT_PROVENANCE.json). The actual pinned TTF/WOFF name tables, converter script, and generated C option headers identify the font inputs used by the compiled 14, 16, 20, 24, 32, and 48 px LVGL fonts. Font Awesome glyphs originate from font files, so their font license applies; its upstream notice also explains the licenses of SVG/JavaScript icons and other Font Awesome assets. Brand names and glyphs retain their owners' trademark status and do not indicate endorsement.

Framework, driver, and library source pins and archive hashes are retained in [docs/TOOLCHAIN_LOCK.json](docs/TOOLCHAIN_LOCK.json). Original headers remain on reused source files. These notices do not replace component-specific source notices or grant a new license to the original application or interface.

Weather data attribution: [Open-Meteo](https://open-meteo.com/). Air quality: Open-Meteo / CAMS ENSEMBLE. Weather and air-quality readings are regional model data. The hosted Open-Meteo free API is for non-commercial use, and its data requires attribution under CC BY 4.0. ECB exchange rates are dated reference rates.

API catalog discovery uses MIT-licensed factual service listings from [public-apis/public-apis](https://github.com/public-apis/public-apis) and [public-api-lists/public-api-lists](https://github.com/public-api-lists/public-api-lists). Their full [license notices and source snapshot provenance](third_party/catalog-discovery/PROVENANCE.json) are included in the source and release package. Provider services retain their own access, data, attribution and usage terms; directory licenses do not license API data.
