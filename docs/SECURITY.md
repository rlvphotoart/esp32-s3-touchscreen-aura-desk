# Read-only security assessment

**2026-10-03 update:** This assessment describes the preserved original firmware/NVS, before AURA Desk replacement. AURA uses pinned Arduino-ESP32 3.1.1 plus its matching high-performance SDK, `DebugLevel=none`, two 5 MiB app slots, and backup-gated serial app-only updates. No eFuse or irreversible security settings were changed. AURA's paired local HTTPS interface uses a self-signed certificate; its transport/access controls do not encrypt stored router settings. See the [user manual](AURA_DESK.md), [build guide](FIRMWARE_BUILD.md), and [release validation](RELEASE_VALIDATION.md) for current behavior and verified tests.

Assessment date: 2026-10-03, Europe/Bucharest. This records the existing device state and a structural audit of the preserved NVS partition. No encryption key, stored name, credential or value was decoded or extracted. No security configuration or eFuse was changed.

## Observed device security state

The recorded ROM security report identifies **Secure Boot disabled** and **Flash Encryption disabled**. The read-only eFuse assessment reports key-block purposes 0–5 as USER/EMPTY rather than an HMAC purpose, and secure version 0. The partition table contains an `nvs` partition at `0x9000`, length `0x6000` (24 KiB), flags 0, and no `nvs_keys` partition. Evidence is retained privately in `logs/security_info.txt`, `logs/efuse_summary_filtered.json` and the original flash backup.

These metadata alone do not settle NVS encryption. Its XTS-AES encryption is a separate layer: the usual flash-encryption-based scheme uses a protected key partition; the HMAC scheme can operate without flash encryption or a key partition. Custom initialization can also supply security configurations directly. A partition's generic encrypted flag is not, by itself, proof of the NVS-layer setting. The recorded absence of the usual key sources is supporting evidence, not the decisive test. [ESP-IDF NVS encryption schemes](https://docs.espressif.com/projects/esp-idf/en/v5.3.2/esp32s3/api-reference/storage/nvs_encryption.html)

## NVS structure and CRC audit

The preserved `backups/nvs.bin` is exactly **24,576 bytes**. Analysis processed it as opaque bytes using the published NVS format. It read only page metadata, entry-state bits, entry span fields and CRC fields; names and value bytes were included only as opaque CRC input. It did not interpret them as text or application data.

NVS uses 4 KiB pages with a 32-byte header, a 32-byte state bitmap and 126 slots of 32 bytes. The audit recomputed page CRCs over bytes 4–27 and item CRCs over bytes 0–3 concatenated with bytes 8–31. Both use the ESP-IDF initial CRC value `0xffffffff`. Continuation slots of multi-slot items were skipped according to a validated header's span, so raw payload slots were not incorrectly classified as independent item headers. [NVS format](https://docs.espressif.com/projects/esp-idf/en/v5.3.2/esp32s3/api-reference/storage/nvs_flash.html#internals), [page CRC implementation](https://github.com/espressif/esp-idf/blob/v5.3.2/components/nvs_flash/src/nvs_page.cpp), [item CRC implementation](https://github.com/espressif/esp-idf/blob/v5.3.2/components/nvs_flash/src/nvs_types.cpp)

| Check | Page 0 | Page 1 | Pages 2–5 |
|---|---:|---:|---|
| Page state | FULL | ACTIVE | Entirely erased (`0xff`) |
| NVS format | v2 (`0xfe`) | v2 (`0xfe`) | Uninitialized |
| Page-header CRC | Valid | Valid | Not applicable |
| Reserved header bytes | All `0xff` | All `0xff` | Not applicable |
| WRITTEN slots | 14 | 62 | 0 |
| ERASED slots | 112 | 27 | 0 |
| EMPTY slots in initialized pages | 0 | 37 | Not applicable |
| Valid current item-header CRCs | 12 | 2 | 0 |
| Payload continuation slots skipped | 2 | 60 | 0 |
| Invalid current item-header CRC candidates | 0 | 0 | 0 |
| Invalid spans/continuation states | 0 | 0 | 0 |

Aggregate: **2 valid initialized page headers, 4 wholly erased pages, 14 valid current item headers, 76 WRITTEN slots and 62 payload continuation slots**. No names, values, namespaces, credential identifiers or per-record content are included in the result. Payload-level CRCs and application meaning were not audited.

## What this establishes

**Strong evidence: standard ESP-IDF NVS XTS-AES encryption is absent from the inspected currently written item records.** The 14 item CRCs validate directly against raw stored bytes without a decryption step. Espressif's standard encrypted implementation encrypts/decrypts complete 32-byte entries, including the item CRC field and its covered bytes. Such ciphertext should not repeatedly validate as ordinary raw NVS item headers. Page-header validity alone would be insufficient because page headers and state bitmaps are kept readable. [Encrypted NVS entry implementation](https://github.com/espressif/esp-idf/blob/v5.3.2/components/nvs_flash/src/nvs_encrypted_partition.cpp)

The conclusion concerns the captured standard NVS container and its current item headers. It does **not** establish that every secret is present there, that any specific Wi-Fi credential is stored, that payloads contain no application-level encrypted blobs, or that all other flash/storage locations are protected or unprotected. Establishing those questions would require a broader audit outside this investigation's scope.

The raw flash/NVS evidence remains private and ignored by Git. This assessment does not enable Secure Boot, Flash Encryption, NVS encryption, anti-rollback or any irreversible provisioning feature.
