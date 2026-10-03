# API services validation — AURA Desk 1.0.5

**Status: passed on the final installed AURA Desk 1.0.5 image. All 22 additional API profiles, native Safari flows and device-rendered Home/Your data frames passed.**

The installed firmware includes the 500-service Browser catalogue and 122 reading configurations. All 500 service entries are browsable with provider documentation, authentication/access scope, formats, use cases and firmware-fit notes. The original 100 reading templates remain available, and 22 new scalar profiles add 22 different services.

The service catalogue and reading catalogue describe different things: **39 of the 500 services have 115 associated reading profiles**. **461 services provide discovery/custom-configuration guidance**. Seven original GitHub/TimeAPI.io readings remain available independently, giving 122 total readings. A service entry does not assert that every provider endpoint is compatible or already implemented.

## Research evidence

| Classification | Count |
|---|---:|
| Provider documentation reviewed | 126 |
| Directory-only discovery | 374 |
| Documented anonymous read scope | 92 |
| Anonymous access reported, requiring confirmation | 404 |
| Optional-key or mixed scope | 3 |
| Authentication unresolved | 1 |
| Potential scalar candidates in original research | 88 |
| Adapter/policy work identified | 32 |
| Further review identified | 380 |

The catalogue has 50 normalized categories and 439 documentation hosts. Its dated `ready_preset=false` and `device_tested=false` flags preserve the original discovery evidence. Separate profile evidence and release tests record actual compatible requests; they do not convert all 500 discoveries into tested integrations.

## Completed software checks

| Check | Result |
|---|---|
| Service/evidence/runtime/licence agreement | 25,521 checks passed |
| Malformed evidence, source and link fixtures | 38 cases rejected |
| Production C++ validation/handler/configuration | 220 assertions across all 22 new profiles and both widget slots |
| Exact embedded Browser JavaScript | 16,732 assertions passed; all 500 services and 122 readings in both slots |
| HTTPS trust/cipher policy | 20 actual-source assertions passed with offline SDK stubs; live handshake gate separate |
| Compiled payload | Exact 493,222-byte runtime payload found once in the application |
| LVGL host regressions | 14 pages, Home/API detail, genuine zero, timers, Browser re-entry, display and keyboard checks passed |

Browser fixtures cover case-insensitive search, no-match feedback, clearing filters, selected-option retention, native select behavior, source/access explanations, draft and enabled-state preservation, saved configuration recognition and pairing/polling/error regressions. Browsing a service alone does not save settings or request that provider.

These are offline software checks. The production C++ tests use platform/network stubs, and host pointer fixtures are not manual operation of the physical touchscreen.

## Initial actual ESP32 fetch pass

All 22 new profiles were submitted to the installed ESP32 through its paired Browser API and fetched in the first widget slot (index 0). **21 succeeded with HTTP 200 and a bounded scalar; GBIF failed with a secure-connection error (HTTP status 0).** The initial gate failed and is retained as a separate historical attempt; the final secure firmware rerun passed all 22 profiles.

The run observed a minimum heap of 31,224 bytes. Both saved widget configurations were restored, and display settings were preserved. Temporary settings writes were used for the test; no firmware or eFuse writes occurred during this fetch pass. Current values, saved configurations, network identity and authentication material are excluded from the public evidence.

| Additional profile | Initial ESP32 result |
|---|---|
| GBIF biodiversity records | Secure connection failed; HTTP status 0 |
| iNaturalist observations | HTTP 200; scalar 9 bytes |
| Ensembl API status | HTTP 200; scalar 1 byte |
| Protein 4HHB resolution | HTTP 200; scalar 4 bytes |
| Caffeine molecular mass | HTTP 200; scalar 6 bytes |
| Gene query symbol | HTTP 200; scalar 4 bytes |
| Figshare article date | HTTP 200; scalar 20 bytes |
| Clinical trial registry ID | HTTP 200; scalar 11 bytes |
| Rick and Morty character | HTTP 200; scalar 12 bytes |
| D&D 2014 ability | HTTP 200; scalar 8 bytes |
| Open5e spell count | HTTP 200; scalar 4 bytes |
| Lichess public blitz rating | HTTP 200; scalar 4 bytes |
| CheapShark first deal price | HTTP 200; scalar 5 bytes |
| Valorant metadata version | HTTP 200; scalar 16 bytes |
| US 90210 latitude | HTTP 200; scalar 7 bytes |
| Public IP example country | HTTP 200; scalar 13 bytes |
| Paris published population | HTTP 200; scalar 7 bytes |
| Brazil state reference | HTTP 200; scalar 14 bytes |
| Boston Red Line reference | HTTP 200; scalar 8 bytes |
| London Victoria line status | HTTP 200; scalar 12 bytes |
| UK Parliament registry count | HTTP 200; scalar 4 bytes |
| Banana nutrition reference | HTTP 200; scalar 2 bytes |

## GBIF TLS reproduction and secure negotiation change

A native host probe built from the [official Mbed TLS 3.6.2 release](https://github.com/Mbed-TLS/mbedtls/releases/tag/mbedtls-3.6.2), matching the pinned SDK library version, reproduced the GBIF failure. It used TLS 1.2, `MBEDTLS_SSL_VERIFY_REQUIRED`, the [official ISRG Root X1](https://letsencrypt.org/certs/isrgrootx1.pem) and the required hostname `api.gbif.org`. The pinned SDK certificate bundle contains the same Root X1 DER subject and public key. No certificate, hostname or authentication checks were disabled.

The exact SDK-like offer used its 121 compiled cipher definitions in preference order, default groups and TLS 1.2 signature algorithms. Mbed TLS filtered unsupported or unavailable suites, leaving **81 advertised cipher-vector entries**, including the renegotiation SCSV. GBIF rejected this ClientHello before ServerHello or certificate delivery with peer fatal alert **`[2:80]` (`internal_error`)**, reported locally as **`-0x7780`**. A clean device retry had already reproduced the fatal alert without concurrent Browser polling or an allocation error.

| Controlled native host offer | Advertised cipher entries, including SCSV | Result |
|---|---:|---|
| Exact SDK-like broad offer; default groups/signatures | 81 | Fatal `internal_error` before ServerHello |
| Broad offer; only groups narrowed to P-256/X25519/P-384 | 81 | Same fatal alert |
| Four ECDHE AES-GCM suites; default groups/signatures | 5 | Certificate verified; HTTP 200 |
| Repeated modern suites, boundary control | 71 | Certificate verified; HTTP 200 |
| Repeated modern suites, boundary control | 72 | Certificate verified; HTTP 200 |
| Repeated modern suites, boundary control | 73 | Fatal `internal_error` before ServerHello |
| Repeated modern suites, boundary control | 74 | Same fatal alert |
| Four-suite offer, ClientHello inflated with ALPN | 5 | Certificate verified; HTTP 200 |

The four-suite control emitted a 137-byte TLS record. Adding an ALPN list increased the same four-suite ClientHello to **353 bytes**, while preserving successful authentication and HTTP 200. The successful 72-entry boundary record was 271 bytes; the failing 73-entry record was 273 bytes. Both halves of the broad suite list also succeeded independently. These controls identify an **observed GBIF peer limit on the advertised cipher-vector count**, rather than a particular unsupported cipher, group, missing trust root or total ClientHello size. They do not identify the peer's server implementation or establish that other providers have the same limit.

The production change first attaches the existing verified certificate bundle, propagates attachment failures, then offers these four unique TLS 1.2 suites using static, zero-terminated storage:

```cpp
static const int suites[] = {
    MBEDTLS_TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
    MBEDTLS_TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
    MBEDTLS_TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
    MBEDTLS_TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
    0
};
mbedtls_ssl_conf_ciphersuites(configuration, suites);
```

Default SDK groups and signature algorithms remain in use. These suites provide ephemeral ECDH and authenticated AES-GCM encryption; the change does not introduce a lower TLS version, unverified trust, an HTTP fallback or a provider-specific hostname exception. The corrected firmware passed the final device fetch, Browser and display gates recorded below.

For a basic reproduction of the TLS failure and single-modern-suite success, build the official source archive and run its unmodified `ssl_client2` example from the release directory:

```sh
curl --fail --location --output isrgrootx1.pem https://letsencrypt.org/certs/isrgrootx1.pem
make -j4 lib
make -C programs -j4 ssl/ssl_client2
./programs/ssl/ssl_client2 server_name=api.gbif.org server_port=443 force_version=tls12 auth_mode=required ca_file=isrgrootx1.pem read_timeout=12000
./programs/ssl/ssl_client2 server_name=api.gbif.org server_port=443 force_version=tls12 auth_mode=required ca_file=isrgrootx1.pem read_timeout=12000 force_ciphersuite=TLS-ECDHE-RSA-WITH-AES-128-GCM-SHA256
```

Those unmodified example commands demonstrate TLS authentication only; their default HTTP/1.0 request does not provide the production Host header. The controlled native probe used `GET /v1/occurrence/search?limit=0 HTTP/1.1`, `Host: api.gbif.org` and `Connection: close` for the HTTP 200 results above. Its boundary controls varied only the cipher vector and retained the same required root, hostname, groups and signatures; its ALPN control varied only the additional ALPN list. Public evidence excludes random handshake bytes, raw provider bodies and private transport logs.

## Final installed-firmware acceptance

| Gate | Verified result |
|---|---|
| Final API pass | All 22 additional profiles returned HTTP 200 and a bounded scalar on the final ESP32 image; minimum observed heap 35,492 bytes |
| Settings restoration | Both saved widget configurations restored after the 22-profile pass; display settings preserved |
| Native Safari catalog | Both native menus contain 500 services and 50 category groups; both unfiltered reading selectors contain 122 templates |
| Search and drafts | Case-insensitive search, no-match feedback, Enter without submission, retained selection, clear-filter restoration and unchanged drafts passed |
| Discovery-only service | RandomDog exposes setup/format/access notes with zero installed readings; browsing does not overwrite any of the five draft fields |
| New Save flows | PubChem caffeine mass saved in slot 0 and Rick and Morty character saved in slot 1; actual device requests succeeded; reload retained the session and recognized both sources |
| Baseline display | Actual Home and Your data frames independently match both saved widget labels, values and units |
| New-reading display | Actual Home and Your data frames independently match both representative new labels, values and units; latest requests HTTP 200 without errors |
| Final restoration | Exact original five-field forms restored in both slots, latest requests succeeded, and final native Safari reload recognized the restored sources |
| Display preferences | Selected brightness 49% and Always-on enabled were preserved throughout final tests |

One earlier complete pass on the cipher-only image returned a generic request-failed-or-timed-out error for iNaturalist, with HTTP status 0. GBIF passed in that attempt; the iNaturalist failure's cause was not established. The full 22-profile repeat used unchanged acceptance checks and passed every profile. An earlier display transfer was also truncated and rejected. Its repeat passed the same frame boundaries, dimensions, pixel SHA-256 and independent regional checks; no incomplete frame was accepted.

Live coverage of all 22 additional profiles uses widget slot 0. The production backend has exhaustive offline coverage in both slots, and native Safari plus device frames verify representative new readings in both slots. Frame checks use the actual ESP32 renderer over UART; they are not camera photographs, optical brightness/color measurements or manual physical touch tests. The exact saved configuration was restored after testing, and the final device was left on Home.

## Sources and privacy

- [Service catalogue](PUBLIC_API_SERVICES.md) and [complete metadata](PUBLIC_API_SERVICES.json)
- [Additional reading profiles](PUBLIC_API_SERVICE_READINGS.json)
- [Generator](../tools/generate_api_services.py) and [independent service checker](../tools/test_api_services.py)
- [Exact Browser regression harness](../tools/test_widget_browser.py)
- [Actual ESP32 profile verifier](../tools/test_api_services_device.py)
- [Structured validation](API_SERVICES_VALIDATION.json)

The public report contains profile identifiers, request outcomes, scalar byte lengths and aggregate health evidence. Private transport logs, owner paths, device/network identifiers, pairing codes, session material, saved configuration, current values and raw API bodies remain outside the public package.
