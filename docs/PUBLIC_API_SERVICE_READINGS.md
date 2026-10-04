# Additional scalar reading examples

These 24 profiles extend the original 100 examples with 24 additional services. The original 22 profiles retain their 3 October 2026 evidence; two profiles were added on 4 October 2026 (Europe/Bucharest). Each selects a real scalar from a successfully parsed public HTTPS JSON response, within the current firmware URL/body/path/text limits. They retain exact request URLs, dot paths, units, refresh intervals and SHA-256 response digests in [PUBLIC_API_SERVICE_READINGS.json](PUBLIC_API_SERVICE_READINGS.json). Raw response bodies and current values are not published.

Each profile records its own desktop check timestamp. The 4 October additions were checked with normal TLS, no credentials and no redirects; body and scalar limits passed. This profile evidence is a desktop snapshot. Actual ESP32 results for the original 22 profiles are in the [1.0.5 baseline](RELEASE_VALIDATION.md); the two additions and browser flow are checked in the [1.0.7 autocomplete report](BROWSER_AUTOCOMPLETE_1.0.7.md). A provider response can change later; the firmware continues to enforce limits and report failures while retaining the last verified value.

| Reading | Service | Exact JSON field | Unit | Refresh | Response bytes | Scalar type / bytes |
|---|---|---|---|---:|---:|---|
| GBIF biodiversity records | [GBIF](https://techdocs.gbif.org/en/openapi/) | `count` | records | 86400 s | 87 | number / 10 |
| iNaturalist observations | [iNaturalist](https://www.inaturalist.org/pages/api+reference) | `total_results` | records | 86400 s | 19525 | number / 9 |
| Ensembl API status | [Ensembl REST](https://rest.ensembl.org/) | `ping` | — | 1800 s | 10 | number / 1 |
| Protein 4HHB resolution | [RCSB Protein Data Bank](https://www.rcsb.org/docs/programmatic-access/web-apis-overview) | `rcsb_entry_info.resolution_combined.0` | angstrom | 86400 s | 26055 | number / 4 |
| Caffeine molecular mass | [PubChem PUG REST](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest) | `PropertyTable.Properties.0.MolecularWeight` | g/mol | 86400 s | 128 | string / 6 |
| Gene query symbol | [MyGene.info](https://docs.mygene.info/en/latest/doc/query_service.html) | `hits.0.symbol` | — | 86400 s | 102 | string / 4 |
| Figshare article date | [Figshare](https://docs.figshare.com/v2/) | `0.published_date` | — | 1800 s | 763 | string / 20 |
| Clinical trial registry ID | [ClinicalTrials.gov](https://clinicaltrials.gov/data-api/api) | `studies.0.protocolSection.identificationModule.nctId` | — | 86400 s | 272 | string / 11 |
| Rick and Morty character | [Rick and Morty API](https://rickandmortyapi.com/documentation) | `name` | — | 86400 s | 2719 | string / 12 |
| D&D 2014 ability | [Dungeons & Dragons 5e SRD API](https://docs.dnd5eapi.co/) | `full_name` | — | 86400 s | 578 | string / 8 |
| Open5e spell count | [Open5e](https://open5e.com/api-docs) | `count` | spells | 86400 s | 2079 | number / 4 |
| Lichess public blitz rating | [Lichess](https://lichess.org/api) | `perfs.blitz.rating` | rating | 1800 s | 1017 | number / 4 |
| CheapShark first deal price | [CheapShark](https://apidocs.cheapshark.com/) | `0.salePrice` | USD | 1800 s | 722 | string / 5 |
| Valorant metadata version | [Valorant-API](https://valorant-api.com/) | `data.version` | — | 86400 s | 363 | string / 16 |
| US 90210 latitude | [Zippopotam.us](https://www.zippopotam.us/) | `places.0.latitude` | deg N | 86400 s | 225 | string / 7 |
| Public IP example country | [GeoJS](https://www.geojs.io/docs/v1/endpoints/geo/) | `country` | — | 86400 s | 292 | string / 13 |
| Paris published population | [France Administrative Geography API](https://geo.api.gouv.fr/) | `population` | people | 86400 s | 51 | number / 7 |
| Brazil state reference | [IBGE Data Service](https://servicodados.ibge.gov.br/api/docs/) | `nome` | — | 86400 s | 94 | string / 14 |
| Boston Red Line reference | [MBTA V3](https://api-v3.mbta.com/docs/swagger/index.html) | `data.attributes.long_name` | — | 86400 s | 499 | string / 8 |
| London Victoria line status | [Transport for London Unified API](https://api-portal.tfl.gov.uk/) | `0.lineStatuses.0.statusSeverityDescription` | — | 1800 s | 2898 | string / 12 |
| UK Parliament registry count | [UK Parliament Members API](https://members-api.parliament.uk/index.html) | `totalResults` | records | 86400 s | 1471 | number / 4 |
| Banana nutrition reference | [Fruityvice](https://www.fruityvice.com/) | `nutritions.calories` | kcal | 86400 s | 169 | number / 2 |
| Meteo.lt Vilnius forecast temperature | [Meteo.lt API](https://api.meteo.lt/) | `forecastTimestamps.0.airTemperature` | °C | 10800 s | 21918 | number / 4 |
| F1 championship leader · Jolpica | [F1 Data API · Jolpica](https://github.com/jolpica/jolpica-f1/blob/main/docs/endpoints/driverStandings.md) | `MRData.StandingsTable.StandingsLists.0.DriverStandings.0.Driver.familyName` | — | 1800 s | 709 | string / 9 |

## Reading context

- **GBIF biodiversity records** — Global count of published biodiversity occurrence records; not a count of species.
- **iNaturalist observations** — Published observation count from a bounded one-item public query. Individual records are not displayed.
- **Ensembl API status** — Public genome API ping: 1 indicates the service responded. This is API availability, not personal genome data.
- **Protein 4HHB resolution** — Experimental resolution of the public 4HHB hemoglobin structure. Reference structure, not a live sensor.
- **Caffeine molecular mass** — Molecular-weight reference for caffeine from PubChem.
- **Gene query symbol** — First gene-symbol match for a public CDK2 query; species and identifiers matter when changing the query.
- **Figshare article date** — Published date of the first public article in a one-item Figshare page. Ordering is provider-defined.
- **Clinical trial registry ID** — Identifier of the first study in a one-item public registry page; no claim that it is the newest study.
- **Rick and Morty character** — Name of public character record 1. Images and long biography fields are not used.
- **D&D 2014 ability** — Full name of the Strength ability from the 2014 D&D SRD API.
- **Open5e spell count** — Count returned by a one-item spell query. Underlying rule sources and editions vary.
- **Lichess public blitz rating** — Public blitz rating for account DrNykterstein; this is a public example account, not the owner of this device.
- **CheapShark first deal price** — Sale price of the first deal returned for store 1. The game can change; check the provider before buying.
- **Valorant metadata version** — Published metadata version from the community Valorant API; this is not an official Riot service.
- **US 90210 latitude** — Latitude for public postcode example US 90210; this is not the device location.
- **Public IP example country** — Approximate GeoJS country for the public example address 8.8.8.8; no owner IP is requested or stored.
- **Paris published population** — Published population for French commune 75056 (Paris). Dataset/reference date applies; this is not a live population count.
- **Brazil state reference** — Name of Brazilian state code 33 from the public IBGE administrative reference.
- **Boston Red Line reference** — Public route name for MBTA route Red. This static example does not claim a live arrival prediction.
- **London Victoria line status** — First reported service-status category for the Victoria line. Multiple disruptions can exist; the full provider response contains more detail.
- **UK Parliament registry count** — Total records returned by the public members search, including historical records; not the number of currently serving MPs.
- **Banana nutrition reference** — Fruityvice nutrition reference for banana. This is a reference value, not a measurement of the user’s portion.

- **Meteo.lt Vilnius forecast temperature** — First hourly temperature in the newest published Vilnius forecast, not a measured current temperature or the device’s saved city. Data source: Lithuanian Hydrometeorological Service (LHMT), under CC BY-SA 4.0; the visible default label includes LHMT attribution.
- **F1 championship leader · Jolpica** — Family name of the first driver in the current-season published championship standings, with a one-result query. This is race standings rather than live lap timing; a season without standings may return no scalar. The current AURA transport already supplies the app/version User-Agent required by Jolpica.

## F1 provider replacement

The original F1 Data API discovery pointed to Jacobbrewer1’s project. Its documented `https://api.bthree.uk/f1/v1/drivers?limit=1` endpoint returned HTTP 404 on 4 October 2026. The `f1-data-api` catalog slot now explicitly names **F1 Data API · Jolpica**, a different provider, and links to its own documentation. The previous provider details and observed failure are retained in `superseded_discovery` and `replacement` metadata; no endpoint from another provider is presented as Jacobbrewer1’s.

## Excluded research samples

No reading template is invented for a failed or unsuitable sample. OpenAlex’s production entitlement is unresolved; Disney’s sample was empty; MeowFacts exceeded the text limit; Scryfall requested a header not set by the current transport; random Cat Facts text still needs repeated Unicode/byte checks. Europe PMC, TLE API and Free Dictionary returned HTTP 503, 508 and 522 respectively during the sample pass.

The 500-service catalogue remains intact, including entries that do not yet have a reading profile. Such entries can be explored through their documentation and configured manually when they meet the current engine requirements.
