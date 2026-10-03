# AURA Desk — 100 public API presets

The Browser includes exactly **100 distinct URL-and-field choices from 19 providers**, grouped in 17 categories. Several choices use different readings from the same provider. This is a curated data catalog, not a claim of 100 independent companies or services.

Use **Find a public API** to search names, providers or topics, then open **Choose a public API · 100 presets**. Selecting a preset fills the label, public HTTPS URL, scalar field, unit and interval and enables the widget. **Save widget** applies it. Browsing and searching do not make provider requests. Both widget slots offer the full catalog.

Saved-city weather and air choices use the device's saved coordinates. Choosing one after changing city refreshes the generated URL. Existing matching saved sources are recognized without changing custom labels, units or intervals. Editing the URL or field clears the old preset attribution. Your own public JSON API remains available.

Each selected preset displays its source explanation and a **Provider documentation** link. Category headings and search counts help narrow the native dropdown. A selected item remains accessible while filtered out; searching does not discard draft fields or submit them when Enter is pressed.

## Categories

| Category | Choices |
| --- | ---: |
| Weather | 18 |
| Air quality | 6 |
| Space | 6 |
| Crypto prices | 7 |
| Currency rates | 15 |
| Crypto market | 8 |
| Bitcoin network | 5 |
| Energy | 3 |
| Earth science | 4 |
| World clocks | 3 |
| Transport | 3 |
| Technology | 4 |
| Books | 4 |
| Games | 5 |
| Words | 3 |
| Country data | 3 |
| Space weather | 3 |

## Verification and behavior

Every catalog URL returned a direct HTTP 200 response over normally verified HTTPS on 2026-10-03. Related fields share cached verification responses. Each chosen field was a non-null number or short string, with a response below 32 KiB and fields within firmware byte limits. All presets need no API key, account or custom header. Saved-city checks used a documented public example location; they do not establish data availability at every coordinate.

Verification records and source links are in [PUBLIC_API_CATALOG.json](PUBLIC_API_CATALOG.json). The build checks the canonical catalog against the exact embedded browser data and refuses stale generation. Actual C++ handler tests exercise each expanded preset in both slots. Browser tests exercise all 100 choices in both slots, search, provider links, saved-source recognition and draft preservation. [Release validation](RELEASE_VALIDATION.md) records the target build, installed image and live Safari/device checks.

Public services can change or rate-limit their feeds. A failed refresh reports its own error and keeps the last successful value with its age; it does not manufacture a zero. Readings are fetched only for the two saved enabled widgets. Refresh intervals follow source publication: weather/market updates, dated currency/country reference data, transport snapshots and static book/game/word records are explained in each hint. Fixed reported years are included in dated country labels.

SpaceX HTTP 525 feeds, oversized Pokémon responses, timed-out requests and sources requiring credentials or unresolved display attribution were excluded. CoinMarketCap's rate-limited dropdown example is replaced by the verified Coinbase Bitcoin preset; an existing custom CoinMarketCap configuration remains editable as Your own API.

Open-Meteo hosted free access is intended for personal non-commercial use, as described in its [terms](https://open-meteo.com/en/terms) and the [manual](AURA_DESK.md). Provider documentation and applicable terms remain authoritative.

## Complete catalog

| # | Choice | Provider | Field | Refresh |
| ---: | --- | --- | --- | ---: |
| 1 | Temperature · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.temperature_2m` | 1800 s |
| 2 | Humidity · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.relative_humidity_2m` | 1800 s |
| 3 | Feels-like temperature · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.apparent_temperature` | 1800 s |
| 4 | Dew point · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.dew_point_2m` | 1800 s |
| 5 | Wind speed · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.wind_speed_10m` | 1800 s |
| 6 | Wind direction · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.wind_direction_10m` | 1800 s |
| 7 | Wind gusts · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.wind_gusts_10m` | 1800 s |
| 8 | Cloud cover · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.cloud_cover` | 1800 s |
| 9 | Sea-level pressure · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.pressure_msl` | 1800 s |
| 10 | Surface pressure · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.surface_pressure` | 1800 s |
| 11 | Precipitation · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.precipitation` | 1800 s |
| 12 | Rain · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.rain` | 1800 s |
| 13 | Snowfall · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.snowfall` | 1800 s |
| 14 | Weather code · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.weather_code` | 1800 s |
| 15 | Daylight flag · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.is_day` | 1800 s |
| 16 | UV index · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `current.uv_index` | 1800 s |
| 17 | Today's high · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `daily.temperature_2m_max.0` | 3600 s |
| 18 | Today's low · saved city | [Open-Meteo](https://open-meteo.com/en/docs) | `daily.temperature_2m_min.0` | 3600 s |
| 19 | European AQI · saved city | [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api) | `current.european_aqi` | 3600 s |
| 20 | US AQI · saved city | [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api) | `current.us_aqi` | 3600 s |
| 21 | PM2.5 · saved city | [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api) | `current.pm2_5` | 3600 s |
| 22 | PM10 · saved city | [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api) | `current.pm10` | 3600 s |
| 23 | Nitrogen dioxide · saved city | [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api) | `current.nitrogen_dioxide` | 3600 s |
| 24 | Ozone · saved city | [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api) | `current.ozone` | 3600 s |
| 25 | Radio blackout · NOAA | [NOAA SWPC](https://www.spaceweather.gov/content/data-access) | `0.R.Scale` | 1800 s |
| 26 | Solar radiation storm · NOAA | [NOAA SWPC](https://www.spaceweather.gov/content/data-access) | `0.S.Scale` | 1800 s |
| 27 | Geomagnetic storm · NOAA | [NOAA SWPC](https://www.spaceweather.gov/content/data-access) | `0.G.Scale` | 1800 s |
| 28 | ISS altitude · Where the ISS at? | [Where the ISS at?](https://wheretheiss.at/w/developer) | `altitude` | 300 s |
| 29 | ISS speed · Where the ISS at? | [Where the ISS at?](https://wheretheiss.at/w/developer) | `velocity` | 300 s |
| 30 | ISS sunlight · Where the ISS at? | [Where the ISS at?](https://wheretheiss.at/w/developer) | `visibility` | 300 s |
| 31 | Bitcoin spot price · Coinbase | [Coinbase](https://docs.cdp.coinbase.com/coinbase-app/track-apis/prices) | `data.amount` | 1800 s |
| 32 | Ethereum spot price · Coinbase | [Coinbase](https://docs.cdp.coinbase.com/coinbase-app/track-apis/prices) | `data.amount` | 1800 s |
| 33 | Solana spot price · Coinbase | [Coinbase](https://docs.cdp.coinbase.com/coinbase-app/track-apis/prices) | `data.amount` | 1800 s |
| 34 | XRP spot price · Coinbase | [Coinbase](https://docs.cdp.coinbase.com/coinbase-app/track-apis/prices) | `data.amount` | 1800 s |
| 35 | Dogecoin spot price · Coinbase | [Coinbase](https://docs.cdp.coinbase.com/coinbase-app/track-apis/prices) | `data.amount` | 1800 s |
| 36 | Cardano spot price · Coinbase | [Coinbase](https://docs.cdp.coinbase.com/coinbase-app/track-apis/prices) | `data.amount` | 1800 s |
| 37 | Litecoin spot price · Coinbase | [Coinbase](https://docs.cdp.coinbase.com/coinbase-app/track-apis/prices) | `data.amount` | 1800 s |
| 38 | EUR / RON · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.RON` | 21600 s |
| 39 | USD / RON · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.RON` | 21600 s |
| 40 | GBP / RON · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.RON` | 21600 s |
| 41 | CHF / RON · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.RON` | 21600 s |
| 42 | EUR / USD · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.USD` | 21600 s |
| 43 | EUR / GBP · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.GBP` | 21600 s |
| 44 | EUR / CHF · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.CHF` | 21600 s |
| 45 | EUR / JPY · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.JPY` | 21600 s |
| 46 | EUR / CAD · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.CAD` | 21600 s |
| 47 | EUR / AUD · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.AUD` | 21600 s |
| 48 | EUR / PLN · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.PLN` | 21600 s |
| 49 | EUR / HUF · Frankfurter | [Frankfurter](https://frankfurter.dev/v1/) | `rates.HUF` | 21600 s |
| 50 | EUR / PLN · NBP | [Narodowy Bank Polski](https://api.nbp.pl/en.html) | `rates.0.mid` | 21600 s |
| 51 | USD / PLN · NBP | [Narodowy Bank Polski](https://api.nbp.pl/en.html) | `rates.0.mid` | 21600 s |
| 52 | Gold per gram · NBP | [Narodowy Bank Polski](https://api.nbp.pl/en.html) | `0.cena` | 21600 s |
| 53 | Bitcoin 24-hour high · Kraken | [Kraken](https://docs.kraken.com/api-reference/market-data/get-ticker-information) | `result.XXBTZUSD.h.1` | 1800 s |
| 54 | Bitcoin 24-hour low · Kraken | [Kraken](https://docs.kraken.com/api-reference/market-data/get-ticker-information) | `result.XXBTZUSD.l.1` | 1800 s |
| 55 | Bitcoin 24-hour volume · Kraken | [Kraken](https://docs.kraken.com/api-reference/market-data/get-ticker-information) | `result.XXBTZUSD.v.1` | 1800 s |
| 56 | Bitcoin 24-hour trades · Kraken | [Kraken](https://docs.kraken.com/api-reference/market-data/get-ticker-information) | `result.XXBTZUSD.t.1` | 1800 s |
| 57 | Bitcoin next-block fee · mempool.space | [mempool.space](https://mempool.space/docs/api/rest) | `fastestFee` | 1800 s |
| 58 | Bitcoin 30-minute fee · mempool.space | [mempool.space](https://mempool.space/docs/api/rest) | `halfHourFee` | 1800 s |
| 59 | Bitcoin one-hour fee · mempool.space | [mempool.space](https://mempool.space/docs/api/rest) | `hourFee` | 1800 s |
| 60 | Bitcoin economy fee · mempool.space | [mempool.space](https://mempool.space/docs/api/rest) | `economyFee` | 1800 s |
| 61 | Bitcoin minimum fee · mempool.space | [mempool.space](https://mempool.space/docs/api/rest) | `minimumFee` | 1800 s |
| 62 | Crypto market capitalization · CoinPaprika | [CoinPaprika](https://docs.coinpaprika.com/api-reference/global/get-market-overview-data) | `market_cap_usd` | 1800 s |
| 63 | Crypto 24-hour volume · CoinPaprika | [CoinPaprika](https://docs.coinpaprika.com/api-reference/global/get-market-overview-data) | `volume_24h_usd` | 1800 s |
| 64 | Bitcoin market dominance · CoinPaprika | [CoinPaprika](https://docs.coinpaprika.com/api-reference/global/get-market-overview-data) | `bitcoin_dominance_percentage` | 1800 s |
| 65 | Active cryptocurrencies · CoinPaprika | [CoinPaprika](https://docs.coinpaprika.com/api-reference/global/get-market-overview-data) | `cryptocurrencies_number` | 1800 s |
| 66 | UK grid carbon forecast · NESO | [UK Carbon Intensity](https://api.carbonintensity.org.uk/) | `data.0.intensity.forecast` | 1800 s |
| 67 | UK grid carbon level · NESO | [UK Carbon Intensity](https://api.carbonintensity.org.uk/) | `data.0.intensity.index` | 1800 s |
| 68 | England grid carbon forecast · NESO | [UK Carbon Intensity](https://api.carbonintensity.org.uk/) | `data.0.data.0.intensity.forecast` | 1800 s |
| 69 | M4.5+ earthquakes / day · USGS | [USGS](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) | `metadata.count` | 1800 s |
| 70 | M5+ earthquakes / 30 days · USGS | [USGS](https://earthquake.usgs.gov/fdsnws/event/1/) | `count` | 21600 s |
| 71 | M6+ earthquakes / 30 days · USGS | [USGS](https://earthquake.usgs.gov/fdsnws/event/1/) | `count` | 21600 s |
| 72 | M7+ earthquakes / 30 days · USGS | [USGS](https://earthquake.usgs.gov/fdsnws/event/1/) | `count` | 21600 s |
| 73 | London time snapshot · TimeAPI | [TimeAPI.io](https://timeapi.io/swagger/) | `time` | 300 s |
| 74 | New York time snapshot · TimeAPI | [TimeAPI.io](https://timeapi.io/swagger/) | `time` | 300 s |
| 75 | Tokyo time snapshot · TimeAPI | [TimeAPI.io](https://timeapi.io/swagger/) | `time` | 300 s |
| 76 | Berlin Hbf next line · VBB | [VBB transport.rest](https://v6.vbb.transport.rest/api.html) | `departures.0.line.name` | 300 s |
| 77 | Berlin Hbf next departure · VBB | [VBB transport.rest](https://v6.vbb.transport.rest/api.html) | `departures.0.when` | 300 s |
| 78 | Berlin Hbf departure mode · VBB | [VBB transport.rest](https://v6.vbb.transport.rest/api.html) | `departures.0.line.product` | 300 s |
| 79 | ESP32 Arduino stars · GitHub | [GitHub](https://docs.github.com/en/rest/repos/repos#get-a-repository) | `stargazers_count` | 21600 s |
| 80 | ESP32 Arduino forks · GitHub | [GitHub](https://docs.github.com/en/rest/repos/repos#get-a-repository) | `forks_count` | 21600 s |
| 81 | LVGL stars · GitHub | [GitHub](https://docs.github.com/en/rest/repos/repos#get-a-repository) | `stargazers_count` | 21600 s |
| 82 | LVGL forks · GitHub | [GitHub](https://docs.github.com/en/rest/repos/repos#get-a-repository) | `forks_count` | 21600 s |
| 83 | Harry Potter book title · Open Library | [Open Library](https://openlibrary.org/dev/docs/api/books) | `title` | 86400 s |
| 84 | Harry Potter reader rating · Open Library | [Open Library](https://openlibrary.org/dev/docs/api/books) | `summary.average` | 86400 s |
| 85 | Harry Potter rating count · Open Library | [Open Library](https://openlibrary.org/dev/docs/api/books) | `summary.count` | 86400 s |
| 86 | Harry Potter five-star votes · Open Library | [Open Library](https://openlibrary.org/dev/docs/api/books) | `counts.5` | 86400 s |
| 87 | Cheri berry growth time · PokéAPI | [PokéAPI](https://pokeapi.co/docs/v2#berries) | `growth_time` | 86400 s |
| 88 | Cheri berry size · PokéAPI | [PokéAPI](https://pokeapi.co/docs/v2#berries) | `size` | 86400 s |
| 89 | Cheri berry max harvest · PokéAPI | [PokéAPI](https://pokeapi.co/docs/v2#berries) | `max_harvest` | 86400 s |
| 90 | Millennium Falcon length · SWAPI | [SWAPI.info](https://swapi.info/documentation) | `length` | 86400 s |
| 91 | Falcon hyperdrive rating · SWAPI | [SWAPI.info](https://swapi.info/documentation) | `hyperdrive_rating` | 86400 s |
| 92 | A rhyme for moon · Datamuse | [Datamuse](https://www.datamuse.com/api/) | `0.word` | 86400 s |
| 93 | A synonym for happy · Datamuse | [Datamuse](https://www.datamuse.com/api/) | `0.word` | 86400 s |
| 94 | An antonym for hot · Datamuse | [Datamuse](https://www.datamuse.com/api/) | `0.word` | 86400 s |
| 95 | Romania population 2024 · World Bank | [World Bank](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures) | `1.0.value` | 86400 s |
| 96 | Romania life expectancy 2023 · World Bank | [World Bank](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures) | `1.0.value` | 86400 s |
| 97 | Romania Internet users 2023 · World Bank | [World Bank](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures) | `1.0.value` | 86400 s |
| 98 | Tomorrow geomagnetic level · NOAA | [NOAA SWPC](https://www.spaceweather.gov/noaa-scales-explanation) | `2.G.Scale` | 1800 s |
| 99 | Tomorrow minor radio chance · NOAA | [NOAA SWPC](https://www.spaceweather.gov/noaa-scales-explanation) | `2.R.MinorProb` | 1800 s |
| 100 | Tomorrow solar storm chance · NOAA | [NOAA SWPC](https://www.spaceweather.gov/noaa-scales-explanation) | `2.S.Prob` | 1800 s |
