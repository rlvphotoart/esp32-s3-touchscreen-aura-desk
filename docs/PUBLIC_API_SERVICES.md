# 500 public API services

AURA Desk includes a searchable catalogue of **500 distinct API services in 50 categories**. The service selector gives each entry a description, provider documentation, access requirements and firmware-fit notes. Services can offer several kinds of data; currency pairs, coins, weather fields and duplicate country feeds are not counted as separate services.

The catalogue preserves all 500 entries from the reviewed source set. Their evidence is retained: **126 provider-documentation reviews and 374 directory discoveries**. There are **92 documented anonymous read scopes**, **404 reported scopes requiring confirmation**, **three optional-key or mixed scopes**, and **one unresolved authentication case**. Public or keyless access does not imply unlimited requests, commercial rights or a perpetual free plan.

For configuration, the Browser retains the original **100 reading templates** and adds **22 bounded scalar examples from 22 additional services**, giving **122 reading choices**. Of these, 115 are associated with 39 catalogue services; seven existing TimeAPI.io/GitHub readings remain available independently. The remaining 461 services provide discovery and setup information rather than a fabricated URL/field combination.

Choose a service to read its setup details. Available reading templates provide a known request and JSON field. Custom configurations still need a public HTTPS JSON endpoint and a short scalar field. Saving the widget applies its configuration and starts a request. A service catalogue entry alone does not assert that the current firmware can use every endpoint the provider offers.

The source-set fit assessment contains 88 scalar candidates, 32 entries needing adapters or policy work, and 380 requiring further review. Its `ready_preset=false` and `device_tested=false` flags describe the original research evidence; separate reading profiles and the release validation report describe actual configuration and test coverage.

- [Complete service metadata](PUBLIC_API_SERVICES.json)
- [Additional reading profiles and exact evidence](PUBLIC_API_SERVICE_READINGS.json)
- [Readable additional reading reference](PUBLIC_API_SERVICE_READINGS.md)
- [Original 100 reading templates](PUBLIC_API_CATALOG.md)
- [Current release validation](RELEASE_VALIDATION.md)

## Scope and limitations

Current widgets accept direct HTTPS 200 GET JSON without credentials or auth headers: at most 200 bytes for the URL, 32 KiB for the response and 47 bytes for the selected scalar. Refresh intervals are at least 300 seconds. XML, GraphQL, RPC, images, identification requirements, attribution, empty results and long text may need additional handling. The full notes for each service are in the JSON and Browser catalogue.

OpenAlex is limited to casual anonymous discovery until production policy is resolved; its provider documentation has different casual and production scopes. Socrata public v2 and authenticated v3 endpoints differ. openFDA has contradictory authentication wording and remains unresolved. Nominatim restricts periodic polling. Nager.Date and Datamuse carry dated hosting/access-policy changes. Attribution and usage terms must be observed wherever applicable.

Services and responses can change after the 3 October 2026 research date. Historical successful requests are evidence for a specific URL and field, not a guarantee that every catalogue service is currently operational.

## Categories

| Category | Services |
|---|---:|
| Animals | 17 |
| Anime | 5 |
| Art & Design | 10 |
| Blockchain | 7 |
| Books | 19 |
| Business | 9 |
| Calendar | 11 |
| Clocks & Time | 1 |
| Cryptocurrency | 24 |
| Currency Exchange | 16 |
| Data Validation | 1 |
| Development | 15 |
| Dictionaries | 6 |
| Documents & Productivity | 4 |
| Earth science | 3 |
| Economics | 4 |
| Education | 2 |
| Email | 5 |
| Energy | 4 |
| Entertainment | 9 |
| Environment | 12 |
| Finance | 14 |
| Food & Drink | 12 |
| Games & Comics | 32 |
| Geocoding | 23 |
| Government | 21 |
| Health | 13 |
| Jobs | 12 |
| Machine Learning | 5 |
| Music | 8 |
| News | 6 |
| Open Data | 14 |
| Open Source Projects | 5 |
| Patent | 1 |
| Personality | 12 |
| Phone | 1 |
| Photography | 5 |
| Science & Math | 24 |
| Security | 7 |
| Shopping | 5 |
| Social | 6 |
| Space & Astronomy | 8 |
| Sports & Fitness | 14 |
| Test Data | 10 |
| Text Analysis | 2 |
| Tracking | 1 |
| Transportation | 19 |
| Vehicle | 5 |
| Video | 14 |
| Weather | 17 |

## Complete service list

Reading counts below include the original and additional profile sets. “Reported” access is not provider confirmation. Detailed constraints, example desktop outcomes and source provenance are preserved in the JSON.

| # | Service and documentation | Category | Access evidence | Firmware fit | Readings | Desk use |
|---:|---|---|---|---|---:|---|
| 1 | [Amazing Endemic Species](https://aes.shenlu.me) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Show a short animal, breed or species reference result from Amazing Endemic Species. |
| 2 | [Axolotl](https://theaxolotlapi.netlify.app/) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Axolotl text item; check length and rendering before use. |
| 3 | [Breed Health Score](https://breedhealthscore.com/developers/) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Show a short animal, breed or species reference result from Breed Health Score. |
| 4 | [Cat Facts](https://alexwohlbruck.github.io/cat-facts/) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Cat Facts text item; check length and rendering before use. |
| 5 | [Cat Facts Ninja](https://catfact.ninja/) | Animals | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Display a short cat fact or the fact length. |
| 6 | [Dog API](https://dogapi.dog) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Dog API text item; check length and rendering before use. |
| 7 | [Dog CEO](https://dog.ceo/dog-api/documentation/) | Animals | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Explore dog breed names or a random dog photograph. |
| 8 | [Dog Facts](https://kinduff.github.io/dog-api/) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Dog Facts text item; check length and rendering before use. |
| 9 | [HTTP Dogs](https://http.dog/) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Show a short animal, breed or species reference result from HTTP Dogs. |
| 10 | [HTTPCat](https://http.cat/) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Show a short animal, breed or species reference result from HTTPCat. |
| 11 | [MeowFacts](https://github.com/wh-iterabb-it/meowfacts) | Animals | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Display a short educational cat fact. |
| 12 | [Movebank](https://github.com/movebank/movebank-api-doc) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Show a short animal, breed or species reference result from Movebank. |
| 13 | [PlaceBear](https://placebear.com/) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a PlaceBear image or visual; this requires an image-capable widget. |
| 14 | [PlaceDog](https://place.dog) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a PlaceDog image or visual; this requires an image-capable widget. |
| 15 | [RandomDog](https://random.dog/woof.json) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a RandomDog image or visual; this requires an image-capable widget. |
| 16 | [RandomDuck](https://random-d.uk/api) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a RandomDuck image or visual; this requires an image-capable widget. |
| 17 | [RandomFox](https://randomfox.ca/floof/) | Animals | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a RandomFox image or visual; this requires an image-capable widget. |
| 18 | [AnimeFacts](https://chandan-02.github.io/anime-facts-rest-api/) | Anime | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short AnimeFacts text item; check length and rendering before use. |
| 19 | [AnimeNewsNetwork](https://www.animenewsnetwork.com/encyclopedia/api.php) | Anime | Reported; confirm access · Directory discovery | Review required | 0 | Show an anime or manga catalogue detail; XML needs conversion. |
| 20 | [AOT quotes](https://attackontitanquotes.vercel.app/) | Anime | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short AOT quotes text item; check length and rendering before use. |
| 21 | [Jikan](https://jikan.moe) | Anime | Reported; confirm access · Directory discovery | Review required | 0 | Show an anime title, rank or score from its public catalogue. |
| 22 | [Studio Ghibli](https://ghibliapi.vercel.app) | Anime | Reported; confirm access · Directory discovery | Review required | 0 | Show a film title, date or character detail. |
| 23 | [Art Institute of Chicago](https://api.artic.edu/docs/) | Art & Design | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Show an artwork title, artist or creation date. |
| 24 | [DummyImage](https://dummyimage.com/) | Art & Design | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a DummyImage image or visual; this requires an image-capable widget. |
| 25 | [eeemoji](https://eeemoji.com/api) | Art & Design | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact art & design result from eeemoji after choosing an appropriate endpoint. |
| 26 | [EmojiHub](https://github.com/cheatsnake/emojihub) | Art & Design | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact art & design result from EmojiHub after choosing an appropriate endpoint. |
| 27 | [Face Shape Guide Lookup](https://myfaceshapechart.com/openapi.json) | Art & Design | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact art & design result from Face Shape Guide Lookup after choosing an appropriate endpoint. |
| 28 | [Icon Horse](https://icon.horse) | Art & Design | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact art & design result from Icon Horse after choosing an appropriate endpoint. |
| 29 | [Iconify](https://iconify.design/docs/api/) | Art & Design | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a Iconify image or visual; this requires an image-capable widget. |
| 30 | [Metropolitan Museum of Art](https://metmuseum.github.io/) | Art & Design | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Display a museum object title, artist or year. |
| 31 | [PHP-Noise](https://php-noise.com/) | Art & Design | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a PHP-Noise image or visual; this requires an image-capable widget. |
| 32 | [The Color API](https://www.thecolorapi.com) | Art & Design | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected color name, hex value or palette detail. |
| 33 | [Blockstream Esplora API](https://github.com/Blockstream/esplora/blob/master/API.md) | Blockchain | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Bitcoin fee estimates, blocks and transaction status |
| 34 | [Chainlink](https://chain.link/developer-resources) | Blockchain | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact blockchain result from Chainlink after choosing an appropriate endpoint. |
| 35 | [Chainpoint](https://tierion.com/chainpoint/) | Blockchain | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact blockchain result from Chainpoint after choosing an appropriate endpoint. |
| 36 | [ClearTrace](https://cleartracedata.com/docs) | Blockchain | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact blockchain result from ClearTrace after choosing an appropriate endpoint. |
| 37 | [Get Started with Web3](https://github.com/beihaili/Get-Started-with-Web3/blob/main/docs/api.md) | Blockchain | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact blockchain result from Get Started with Web3 after choosing an appropriate endpoint. |
| 38 | [mempool.space REST API](https://mempool.space/docs/api/rest) | Blockchain | Documented public scope · Provider docs reviewed | Scalar candidate | 5 | Recommended Bitcoin transaction fee and network statistics |
| 39 | [TWZRD Agent Intel](https://intel.twzrd.xyz) | Blockchain | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact blockchain result from TWZRD Agent Intel after choosing an appropriate endpoint. |
| 40 | [Al Quran Cloud](https://alquran.cloud/api) | Books | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Show a verse reference, chapter name or selected translation. |
| 41 | [Bible-api](https://bible-api.com/) | Books | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Show a selected verse reference or short reading. |
| 42 | [Crossref Metadata Search](https://github.com/CrossRef/rest-api-doc) | Books | Reported; confirm access · Directory discovery | Review required | 0 | Show a scholarly publication title, year or DOI metadata. |
| 43 | [Greenlit Books](https://greenlitbooks.com/developers) | Books | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Greenlit Books catalogue item or selected numeric detail. |
| 44 | [Gutendex](https://gutendex.com/) | Books | Reported; confirm access · Provider docs reviewed | Scalar candidate | 0 | Show a public-domain ebook title or download count. |
| 45 | [Harry Potter API](https://github.com/fedeperin/potterapi) | Books | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Harry Potter API catalogue item or selected numeric detail. |
| 46 | [KDP Intelligence](https://kdp-intelligence-api.vercel.app/docs) | Books | Reported; confirm access · Directory discovery | Review required | 0 | Show a short KDP Intelligence catalogue item or selected numeric detail. |
| 47 | [Library of Congress](https://www.loc.gov/apis/) | Books | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Show collection search totals or a historic item title. |
| 48 | [Nobel Prize](https://www.nobelprize.org/organization/developer-zone-2/) | Books | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Display a Nobel laureate, award year or category. |
| 49 | [Open Library](https://openlibrary.org/developers/api) | Books | Reported; confirm access · Provider docs reviewed | Scalar candidate | 4 | Display a book title, author or reading discovery count. |
| 50 | [PoetryDB](https://github.com/thundercomb/poetrydb) | Books | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Display a poem title, poet or line count. |
| 51 | [Quran](https://quran.api-docs.io/) | Books | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Quran catalogue item or selected numeric detail. |
| 52 | [Quran-api](https://github.com/fawazahmed0/quran-api#readme) | Books | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Quran-api catalogue item or selected numeric detail. |
| 53 | [Rig Veda](https://aninditabasu.github.io/indica/) | Books | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Rig Veda catalogue item or selected numeric detail. |
| 54 | [Runyankole Bible](https://runyankole-bible-api.vercel.app) | Books | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Runyankole Bible catalogue item or selected numeric detail. |
| 55 | [Thirukkural](https://api-thirukkural.web.app/) | Books | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Thirukkural catalogue item or selected numeric detail. |
| 56 | [Urantia Papers](https://urantia.dev) | Books | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Urantia Papers catalogue item or selected numeric detail. |
| 57 | [Wikimedia Action API](https://www.mediawiki.org/wiki/API:Main_page) | Books | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Display a short article title or public encyclopedia statistic. |
| 58 | [Wolne Lektury](https://wolnelektury.pl/api/) | Books | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Display a Polish classic book title or author. |
| 59 | [Auregistre](https://auregistre.fr/api) | Business | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected public organisation or product-lookup detail from Auregistre. |
| 60 | [Domainsdb.info](https://domainsdb.info/) | Business | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected public organisation or product-lookup detail from Domainsdb.info. |
| 61 | [KontragentPro](https://kontragentpro.ru/api/v2/docs) | Business | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected public organisation or product-lookup detail from KontragentPro. |
| 62 | [Legal Sandbox Georgia](https://legal.ge/api/openapi.json) | Business | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected public organisation or product-lookup detail from Legal Sandbox Georgia. |
| 63 | [Markbase](https://markbase.co) | Business | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected public organisation or product-lookup detail from Markbase. |
| 64 | [Mydentify](https://mydentify.com/openapi.json) | Business | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected public organisation or product-lookup detail from Mydentify. |
| 65 | [Pick an Agency](https://www.pickanagency.com/developers) | Business | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected public organisation or product-lookup detail from Pick an Agency. |
| 66 | [SCALA Score](https://score.get-scala.com) | Business | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected public organisation or product-lookup detail from SCALA Score. |
| 67 | [SEC EDGAR Data API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | Business | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Filings and structured company financial statements |
| 68 | [Byabbe](https://byabbe.se/on-this-day/#/default/get__month___day__events_json) | Calendar | Reported; confirm access · Directory discovery | Review required | 0 | Show a date, calendar event or non-working-day detail from Byabbe. |
| 69 | [caldays](https://caldays.com/api) | Calendar | Reported; confirm access · Directory discovery | Review required | 0 | Show a date, calendar event or non-working-day detail from caldays. |
| 70 | [Nager.Date](https://github.com/nager/Nager.Date) | Calendar | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Show the next public holiday for a chosen country. |
| 71 | [Namedays Calendar](https://nameday.abalin.net) | Calendar | Reported; confirm access · Directory discovery | Review required | 0 | Show a date, calendar event or non-working-day detail from Namedays Calendar. |
| 72 | [Non-working Days](https://isdayoff.ru) | Calendar | Reported; confirm access · Directory discovery | Review required | 0 | Show a date, calendar event or non-working-day detail from Non-working Days. |
| 73 | [Non-Working Days ICS](https://github.com/gadael/icsdb) | Calendar | Reported; confirm access · Directory discovery | Review required | 0 | Show a date, calendar event or non-working-day detail from Non-Working Days ICS. |
| 74 | [OpenHolidays API](https://www.openholidaysapi.org/) | Calendar | Reported; confirm access · Directory discovery | Review required | 0 | Show a public or school holiday date for a selected region. |
| 75 | [Russian Calendar](https://github.com/egno/work-calendar) | Calendar | Reported; confirm access · Directory discovery | Review required | 0 | Show a date, calendar event or non-working-day detail from Russian Calendar. |
| 76 | [The Calendar](https://the-calendar.net/api/) | Calendar | Reported; confirm access · Directory discovery | Review required | 0 | Show a date, calendar event or non-working-day detail from The Calendar. |
| 77 | [TimeZones iCal Library](https://tz.add-to-calendar-technology.com/) | Calendar | Reported; confirm access · Directory discovery | Review required | 0 | Show a date, calendar event or non-working-day detail from TimeZones iCal Library. |
| 78 | [UK Bank Holidays](https://www.gov.uk/bank-holidays.json) | Calendar | Reported; confirm access · Directory discovery | Review required | 0 | Count down to an official U.K. bank holiday. |
| 79 | [timezone.io WorldTime-compatible API](https://www.timezone.io/docs/worldtimeapi) | Clocks & Time | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Current time and daylight-saving metadata |
| 80 | [Alpha (Mossland)](https://alpha.moss.land/developers) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from Alpha (Mossland) after choosing a public read endpoint. |
| 81 | [Binance Spot Public Data](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general) | Cryptocurrency | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Exchange spot prices and market summaries |
| 82 | [Bitcoin Halving](https://why21million.com/halving-api/) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from Bitcoin Halving after choosing a public read endpoint. |
| 83 | [Bitfinex Public API](https://docs.bitfinex.com/docs/introduction) | Cryptocurrency | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Market ticker and candle observations |
| 84 | [Bitstamp Public Market API](https://www.bitstamp.net/api/) | Cryptocurrency | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Ticker, spread and volume on supported markets |
| 85 | [Block Lottos](https://blocklottos.com/openapi.json) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from Block Lottos after choosing a public read endpoint. |
| 86 | [BTCGlobe](https://btcglobe.live/join#makers) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from BTCGlobe after choosing a public read endpoint. |
| 87 | [btcnode.uk](https://btcnode.uk) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from btcnode.uk after choosing a public read endpoint. |
| 88 | [Bybit Market API](https://bybit-exchange.github.io/docs/v5/market/tickers) | Cryptocurrency | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Spot and derivative ticker readings |
| 89 | [Coinbase Prices API](https://docs.cdp.coinbase.com/coinbase-app/track-apis/prices) | Cryptocurrency | Documented public scope · Provider docs reviewed | Scalar candidate | 7 | Spot exchange price for a chosen trading pair |
| 90 | [CoinLobster](https://coinlobster.com/developers) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from CoinLobster after choosing a public read endpoint. |
| 91 | [Coinlore](https://www.coinlore.com/cryptocurrency-data-api) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track a cryptocurrency price or market statistic. |
| 92 | [CoinPaprika API](https://docs.coinpaprika.com/) | Cryptocurrency | Documented public scope · Provider docs reviewed | Scalar candidate | 4 | Coin prices and global crypto market metrics |
| 93 | [CoinRanking](https://docs.coinranking.com/) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from CoinRanking after choosing a public read endpoint. |
| 94 | [CorpStacking](https://www.corpstacking.com/feed.json) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from CorpStacking after choosing a public read endpoint. |
| 95 | [CryptAPI](https://docs.cryptapi.io/) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from CryptAPI after choosing a public read endpoint. |
| 96 | [Crypto Fear & Greed Index (qiaobax)](https://qiaobax.com/en/tools/fear-greed-index/) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from Crypto Fear & Greed Index (qiaobax) after choosing a public read endpoint. |
| 97 | [Dudelytics](https://dudelytics.com/en/dpmi/data/) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from Dudelytics after choosing a public read endpoint. |
| 98 | [FraudCoins](https://fraudcoins.com/data/) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track one reported blockchain or market value from FraudCoins after choosing a public read endpoint. |
| 99 | [Gemini](https://docs.gemini.com/rest-api/) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Track a public exchange ticker or recent market trade. |
| 100 | [Kraken Public Market Data](https://docs.kraken.com/api-reference/market-data/get-ticker-information) | Cryptocurrency | Documented public scope · Provider docs reviewed | Scalar candidate | 4 | Exchange ticker, bid/ask and daily volume |
| 101 | [KuCoin Market API](https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-ticker) | Cryptocurrency | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Single-market ticker and bid/ask quotes |
| 102 | [MEXC Spot Market API](https://mexcdevelop.github.io/apidocs/spot_v3_en/) | Cryptocurrency | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Spot ticker and public market observations |
| 103 | [Solana JSON RPC](https://docs.solana.com/developing/clients/jsonrpc-api) | Cryptocurrency | Reported; confirm access · Directory discovery | Review required | 0 | Show a public blockchain status metric; RPC needs an adapter. |
| 104 | [Bank of Canada Valet API](https://www.bankofcanada.ca/valet-api-how-to/) | Currency Exchange | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Official exchange rates, interest rates and economic series |
| 105 | [Bank of Russia](https://www.cbr.ru/development/SXML/) | Currency Exchange | Reported; confirm access · Directory discovery | Review required | 0 | Show a Russian central-bank reference rate; XML needs conversion. |
| 106 | [Cambio Uruguay](https://cambio-uruguay.com) | Currency Exchange | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from Cambio Uruguay. |
| 107 | [Czech National Bank](https://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.xml) | Currency Exchange | Reported; confirm access · Directory discovery | Review required | 0 | Show a Czech central-bank reference exchange rate. |
| 108 | [Daleelak](https://getdaleelak.com/en/api) | Currency Exchange | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from Daleelak. |
| 109 | [ECB Data Portal API](https://data.ecb.europa.eu/help/api/data) | Currency Exchange | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Official exchange rates and monetary statistics |
| 110 | [Economia.Awesome](https://docs.awesomeapi.com.br/api-de-moedas) | Currency Exchange | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from Economia.Awesome. |
| 111 | [ExchangeRate-API Open Access](https://www.exchangerate-api.com/docs/free) | Currency Exchange | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Daily exchange-rate snapshot |
| 112 | [Exchangerate.dev](https://exchangerate.dev/docs) | Currency Exchange | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from Exchangerate.dev. |
| 113 | [Fawaz Ahmed Currency API](https://github.com/fawazahmed0/exchange-api) | Currency Exchange | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Daily open currency-rate snapshots |
| 114 | [Frankfurter](https://frankfurter.dev/) | Currency Exchange | Documented public scope · Provider docs reviewed | Scalar candidate | 12 | Central-bank-backed foreign exchange rates |
| 115 | [Fulusly](https://fulusly.soft9.us/developers) | Currency Exchange | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from Fulusly. |
| 116 | [FXpeek](https://fxpeek.com/en/api) | Currency Exchange | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from FXpeek. |
| 117 | [NBP Web API](https://api.nbp.pl/en.html) | Currency Exchange | Documented public scope · Provider docs reviewed | Scalar candidate | 3 | Official PLN exchange rates and gold prices |
| 118 | [paralelo.bo](https://paralelo.bo/api) | Currency Exchange | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from paralelo.bo. |
| 119 | [Riksbank Rates API](https://developer.api.riksbank.se/) | Currency Exchange | Optional / mixed key scope · Provider docs reviewed | Review required | 0 | Official Swedish interest and currency rates |
| 120 | [NumValidate](https://numvalidate.com) | Data Validation | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact data validation result from NumValidate after choosing an appropriate endpoint. |
| 121 | [24 Pull Requests](https://24pullrequests.com/api) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show one development-tool, package or public service-status result from 24 Pull Requests. |
| 122 | [Abacus](https://abacus.jasoncameron.dev) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show one development-tool, package or public service-status result from Abacus. |
| 123 | [Agent Nexus](https://agentnexus.app/llms.txt) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show one development-tool, package or public service-status result from Agent Nexus. |
| 124 | [CDNJS](https://api.cdnjs.com/libraries/jquery) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show the latest available version of a chosen web library. |
| 125 | [Cloudflare Trace](https://github.com/fawazahmed0/cloudflare-trace-api) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show connection information; text responses need conversion. |
| 126 | [DigitalOcean Status](https://status.digitalocean.com/api/v2) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show a public service status or incident summary. |
| 127 | [Go Module Proxy](https://go.dev/ref/mod#goproxy-protocol) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show a chosen Go module version or timestamp. |
| 128 | [Homebrew Formulae](https://formulae.brew.sh/api/) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show a package version or package metadata statistic. |
| 129 | [jsDelivr](https://github.com/jsdelivr/data.jsdelivr.com) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show a package version or CDN download statistic. |
| 130 | [NetworkCalc](https://networkcalc.com/api/docs) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show a DNS lookup or selected network calculation result. |
| 131 | [npm Registry](https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected JavaScript package version or metadata value. |
| 132 | [NuGet](https://learn.microsoft.com/en-us/nuget/api/overview) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected .NET package version or metadata value. |
| 133 | [Open VSX](https://open-vsx.org/) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show a chosen editor extension version or download count. |
| 134 | [Packagist](https://packagist.org/apidoc) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show a chosen PHP package version or metadata statistic. |
| 135 | [RubyGems](https://guides.rubygems.org/rubygems-org-api/) | Development | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected Ruby package version or download count. |
| 136 | [Chinese Text Project](https://ctext.org/tools/api) | Dictionaries | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact dictionaries result from Chinese Text Project after choosing an appropriate endpoint. |
| 137 | [Datamuse](https://www.datamuse.com/api/) | Dictionaries | Documented public scope · Provider docs reviewed | Scalar candidate | 3 | Show a related word, rhyme or vocabulary suggestion. |
| 138 | [Free Dictionary API](https://dictionaryapi.dev/) | Dictionaries | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Show pronunciation metadata or a short vocabulary definition. |
| 139 | [Random Lexicon](https://randomlexicon.com/api-reference) | Dictionaries | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact dictionaries result from Random Lexicon after choosing an appropriate endpoint. |
| 140 | [Wiktionary](https://en.wiktionary.org/w/api.php) | Dictionaries | Reported; confirm access · Directory discovery | Review required | 0 | Show a short language or word entry after parsing the response. |
| 141 | [WordSoHard](https://wordsohard.com/api) | Dictionaries | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact dictionaries result from WordSoHard after choosing an appropriate endpoint. |
| 142 | [AgentPay Doc Tools](https://agentpay-tools.agentpay-apis.workers.dev) | Documents & Productivity | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact documents & productivity result from AgentPay Doc Tools after choosing an appropriate endpoint. |
| 143 | [DocStruct](https://docstruct.pages.dev) | Documents & Productivity | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact documents & productivity result from DocStruct after choosing an appropriate endpoint. |
| 144 | [IDPhotoSnap Passport Photo Specs](https://idphotosnap.com/api/specs) | Documents & Productivity | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a IDPhotoSnap Passport Photo Specs image or visual; this requires an image-capable widget. |
| 145 | [Vector Express v2.0](https://vector.express) | Documents & Productivity | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact documents & productivity result from Vector Express v2.0 after choosing an appropriate endpoint. |
| 146 | [Environment Agency Flood-monitoring](https://environment.data.gov.uk/flood-monitoring/doc/reference) | Earth science | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | River levels, rainfall and flood status |
| 147 | [NASA EONET](https://eonet.gsfc.nasa.gov/docs/v3) | Earth science | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Natural-event metadata and locations |
| 148 | [USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/) | Earth science | Documented public scope · Provider docs reviewed | Scalar candidate | 4 | Recent earthquake count and selected event properties |
| 149 | [BLS Public Data API](https://www.bls.gov/developers/) | Economics | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Inflation and employment observations |
| 150 | [Eurostat Dissemination API](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-detailed-guidelines) | Economics | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | European economic and social statistics |
| 151 | [Statistics Canada Web Data Service](https://www.statcan.gc.ca/en/developers/wds) | Economics | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Canadian economic and demographic statistics |
| 152 | [World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation) | Economics | Documented public scope · Provider docs reviewed | Scalar candidate | 3 | Country development and economic indicators |
| 153 | [College ROI](https://le-teen.com/api) | Education | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact education result from College ROI after choosing an appropriate endpoint. |
| 154 | [NationNode](https://nationnode.vercel.app) | Education | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact education result from NationNode after choosing an appropriate endpoint. |
| 155 | [Best Temp Mail](https://best-tempmail.com/api) | Email | Reported; confirm access · Directory discovery | Review required | 0 | Show an email or domain validation result from Best Temp Mail; this needs a separate tool flow. |
| 156 | [Disify](https://www.disify.com/) | Email | Reported; confirm access · Directory discovery | Review required | 0 | Show an email or domain validation result from Disify; this needs a separate tool flow. |
| 157 | [DropMail](https://dropmail.me/api/#live-demo) | Email | Reported; confirm access · Directory discovery | Review required | 0 | Show an email or domain validation result from DropMail; this needs a separate tool flow. |
| 158 | [Email Spam Tester](https://email-spam-tester.com/api-docs/) | Email | Reported; confirm access · Directory discovery | Review required | 0 | Show an email or domain validation result from Email Spam Tester; this needs a separate tool flow. |
| 159 | [Guerrilla Mail](https://www.guerrillamail.com/GuerrillaMailAPI.html) | Email | Reported; confirm access · Directory discovery | Review required | 0 | Show an email or domain validation result from Guerrilla Mail; this needs a separate tool flow. |
| 160 | [Elexon Insights API](https://developer.data.elexon.co.uk/) | Energy | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | GB demand, generation and system-frequency data |
| 161 | [Energi Data Service](https://www.energidataservice.dk/guides/api-guides) | Energy | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Danish electricity, emissions and spot-price statistics |
| 162 | [Octopus Energy Public Products API](https://docs.octopus.energy/rest/guides/endpoints/) | Energy | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | UK energy tariffs and standing/unit charges |
| 163 | [UK Carbon Intensity API](https://carbonintensity.org.uk/) | Energy | Documented public scope · Provider docs reviewed | Adapter / policy work | 3 | GB generation mix and carbon-intensity estimate |
| 164 | [Bucketlist Dream of the Day](https://bucketlist.nl/samenwerken?lang=en#droom-van-de-dag) | Entertainment | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a Bucketlist Dream of the Day image or visual; this requires an image-capable widget. |
| 165 | [Corporate Buzz Words](https://github.com/sameerkumar18/corporate-bs-generator-api) | Entertainment | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact entertainment result from Corporate Buzz Words after choosing an appropriate endpoint. |
| 166 | [CosmyDay Astrology](https://cosmyday.com/api-docs) | Entertainment | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact entertainment result from CosmyDay Astrology after choosing an appropriate endpoint. |
| 167 | [Fun Fact](https://api.aakhilv.me) | Entertainment | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Fun Fact text item; check length and rendering before use. |
| 168 | [Imgflip](https://imgflip.com/api) | Entertainment | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact entertainment result from Imgflip after choosing an appropriate endpoint. |
| 169 | [justmeme.wtf](https://justmeme.wtf/api-docs) | Entertainment | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact entertainment result from justmeme.wtf after choosing an appropriate endpoint. |
| 170 | [Meme Maker](https://mememaker.github.io/API/) | Entertainment | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact entertainment result from Meme Maker after choosing an appropriate endpoint. |
| 171 | [Techy](https://techy-api.vercel.app/) | Entertainment | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact entertainment result from Techy after choosing an appropriate endpoint. |
| 172 | [Yo Momma Jokes](https://github.com/beanboi7/yomomma-apiv2) | Entertainment | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Yo Momma Jokes text item; check length and rendering before use. |
| 173 | [CO2 Offset](https://co2offset.io/api.html) | Environment | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from CO2 Offset. |
| 174 | [DC Hub](https://dchub.cloud/playground) | Environment | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from DC Hub. |
| 175 | [EPA Envirofacts Data Service](https://www.epa.gov/enviro/envirofacts-data-service-api) | Environment | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Facility emissions and environmental statistics |
| 176 | [kanari](https://kanari.io/en/api) | Environment | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from kanari. |
| 177 | [Luchtmeetnet](https://api-docs.luchtmeetnet.nl/) | Environment | Reported; confirm access · Directory discovery | Review required | 0 | Track an official Dutch air-quality measurement. |
| 178 | [openSenseMap API](https://api.opensensemap.org/) | Environment | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Community environmental sensor measurements |
| 179 | [PM2.5 Open Data Portal](https://pm25.lass-net.org/#apis) | Environment | Reported; confirm access · Directory discovery | Review required | 0 | Show a reported particulate air-quality measurement. |
| 180 | [PVGIS](https://joint-research-centre.ec.europa.eu/pvgis-photovoltaic-geographical-information-system/getting-started-pvgis/api-non-interactive-service) | Environment | Reported; confirm access · Directory discovery | Review required | 0 | Show a solar-resource or photovoltaic-yield estimate. |
| 181 | [Sensor.Community Data API](https://github.com/opendata-stuttgart/meta/wiki/APIs) | Environment | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Local community particulate and weather readings |
| 182 | [Solematica](https://www.solematica.it/sviluppatori) | Environment | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a Solematica image or visual; this requires an image-capable widget. |
| 183 | [USGS Water Services](https://waterservices.usgs.gov/) | Environment | Reported; confirm access · Provider docs reviewed | Scalar candidate | 0 | Track river level or streamflow at a selected gauging station. |
| 184 | [Website Carbon](https://api.websitecarbon.com/) | Environment | Reported; confirm access · Directory discovery | Review required | 0 | Show a website carbon-estimate value or rating. |
| 185 | [aikstockdata](https://aikstockdata.com/en/api) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from aikstockdata. |
| 186 | [AlphaSMO](https://alphasmo.com/developer/docs) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from AlphaSMO. |
| 187 | [Banking Access Index](https://www.globalsolo.global/data/banking-access-index) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from Banking Access Index. |
| 188 | [contix](https://contix.es/api/#herramientas) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from contix. |
| 189 | [EstimateTax](https://estimatetax.net/api/) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from EstimateTax. |
| 190 | [Finance Clearly Tax Rates](https://financeclearly.com/tax-rates-api/) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from Finance Clearly Tax Rates. |
| 191 | [Indian Bank Data API](https://github.com/kaustubhk24/Indian-Banks-Data) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from Indian Bank Data API. |
| 192 | [KeepRule](https://github.com/henu-wang/keeprule-api) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short KeepRule text item; check length and rendering before use. |
| 193 | [LiquiLens](https://liquilens.in/developers/) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from LiquiLens. |
| 194 | [MyPayslip.lk](https://mypayslip.lk/openapi.json) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from MyPayslip.lk. |
| 195 | [Open Economics](https://open-economics-data.knbf982hkn.chatgpt.site/en/docs) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from Open Economics. |
| 196 | [Polish Bank Branches](https://ksefekburczymucha.pl/api/bank/) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from Polish Bank Branches. |
| 197 | [PolyKal Fees](https://polymarket-kalshi.com/fee-schedule/) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected rate, market measure or published reference value from PolyKal Fees. |
| 198 | [Razorpay IFSC](https://ifsc.razorpay.com/) | Finance | Reported; confirm access · Directory discovery | Review required | 0 | Show an Indian bank branch, location or IFSC lookup result. |
| 199 | [BaconMockup](https://baconmockup.com/) | Food & Drink | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a BaconMockup image or visual; this requires an image-capable widget. |
| 200 | [Coffee](https://coffee.alexflipnote.dev/) | Food & Drink | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a Coffee image or visual; this requires an image-capable widget. |
| 201 | [Daily Food Recalls](https://dailyfoodrecalls.com/api/) | Food & Drink | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact food & drink result from Daily Food Recalls after choosing an appropriate endpoint. |
| 202 | [ExactCup](https://exactcup.github.io/api/) | Food & Drink | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact food & drink result from ExactCup after choosing an appropriate endpoint. |
| 203 | [Foodish](https://github.com/surhud004/Foodish#readme) | Food & Drink | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a Foodish image or visual; this requires an image-capable widget. |
| 204 | [Fruityvice](https://www.fruityvice.com/) | Food & Drink | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show calories or a nutrient for a selected fruit. |
| 205 | [Open Brewery DB](https://www.openbrewerydb.org/documentation) | Food & Drink | Reported; confirm access · Provider docs reviewed | Scalar candidate | 0 | Show a brewery name or city from a chosen region. |
| 206 | [Open Food Facts](https://openfoodfacts.github.io/openfoodfacts-server/api/) | Food & Drink | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Show a packaged food label, nutrition score or selected nutrient. |
| 207 | [PunkAPI](https://github.com/alxiw/punkapi) | Food & Drink | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact food & drink result from PunkAPI after choosing an appropriate endpoint. |
| 208 | [Racion](https://racion.app/developers) | Food & Drink | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact food & drink result from Racion after choosing an appropriate endpoint. |
| 209 | [The Report of the Week](https://github.com/andyklimczak/TheReportOfTheWeek-API) | Food & Drink | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact food & drink result from The Report of the Week after choosing an appropriate endpoint. |
| 210 | [WhiskyHunter](https://whiskyhunter.net/api/) | Food & Drink | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact food & drink result from WhiskyHunter after choosing an appropriate endpoint. |
| 211 | [AmiiboAPI](https://www.amiiboapi.com/) | Games & Comics | Reported; confirm access · Provider docs reviewed | Scalar candidate | 0 | Show an amiibo character name, game series or release date. |
| 212 | [Astroworld](https://api.astroworldmc.com) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Astroworld catalogue item or selected numeric detail. |
| 213 | [Autochess VNG](https://github.com/didadadida93/autochess-vng-api) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Autochess VNG catalogue item or selected numeric detail. |
| 214 | [Barter.VG](https://github.com/bartervg/barter.vg/wiki) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected game trading or catalogue metadata value. |
| 215 | [Blue Archive](https://github.com/arufars/api-blue-archive) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Blue Archive catalogue item or selected numeric detail. |
| 216 | [CheapShark](https://apidocs.cheapshark.com/) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show a selected PC game deal or price change. |
| 217 | [Chess.com Published Data](https://www.chess.com/news/view/published-data-api) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Track a public chess rating, daily puzzle title or player statistic. |
| 218 | [Disney API](https://disneyapi.dev/docs/) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Display a Disney character name or film association. |
| 219 | [Dota 2](https://docs.opendota.com/) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a public game or player statistic after mapping an endpoint. |
| 220 | [Dungeons & Dragons 5e SRD API](https://docs.dnd5eapi.co/) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show a rule name, spell level or monster statistic. |
| 221 | [FFXIV Collect](https://ffxivcollect.com/) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected achievement or collection-count statistic. |
| 222 | [FreeToGame](https://www.freetogame.com/api-doc) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Show a free-to-play game title, platform or release date. |
| 223 | [GamerPower](https://www.gamerpower.com/api-read) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Track giveaway totals or a selected free-game offer. |
| 224 | [GW2Spidy](https://github.com/rubensayshi/gw2spidy/wiki) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a Guild Wars 2 item price or trading statistic. |
| 225 | [Hyrule Compendium](https://github.com/gadhagod/Hyrule-Compendium-API) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a Zelda creature or item detail. |
| 226 | [JokeAPI](https://sv443.net/jokeapi/v2/) | Games & Comics | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Display a category or a daily joke. |
| 227 | [Lichess](https://lichess.org/api) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Track a public chess rating or player activity. |
| 228 | [Minecraft Server Status](https://api.mcsrvstat.us) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a chosen server online state or player count. |
| 229 | [Monster Hunter World](https://docs.mhw-db.com/) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a monster, weapon or armour statistic. |
| 230 | [Open Trivia Database](https://opentdb.com/api_config.php) | Games & Comics | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Show a daily trivia category, question count or selected question. |
| 231 | [Open5e](https://open5e.com/api-docs) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show a tabletop spell, monster challenge rating or equipment fact. |
| 232 | [PokéAPI](https://pokeapi.co/docs/v2) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 3 | Show a Pokémon name, height, weight or base statistic. |
| 233 | [Rick and Morty API](https://rickandmortyapi.com/documentation) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show a character name, species or current catalogue count. |
| 234 | [RuneScape](https://runescape.wiki/w/Application_programming_interface) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a public game or item statistic. |
| 235 | [Scryfall](https://scryfall.com/docs/api) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Display a Magic card name, set or mana value. |
| 236 | [SWAPI](https://swapi.info/) | Games & Comics | Reported; confirm access · Provider docs reviewed | Scalar candidate | 2 | Display a Star Wars character or spacecraft parameter. |
| 237 | [TCGdex](https://www.tcgdex.dev/) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a Pokémon card or set detail. |
| 238 | [TETR.IO](https://tetr.io/about/api/) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a public player rank, rating or game statistic. |
| 239 | [Universalis](https://universalis.app/docs/index.html) | Games & Comics | Reported; confirm access · Directory discovery | Review required | 0 | Show a Final Fantasy XIV item price or market statistic. |
| 240 | [Valorant-API](https://valorant-api.com/) | Games & Comics | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show game content version, agent name or weapon metadata. |
| 241 | [xkcd](https://xkcd.com/json.html) | Games & Comics | Reported; confirm access · Provider docs reviewed | Scalar candidate | 0 | Show the latest comic number or title. |
| 242 | [YGOPRODeck](https://ygoprodeck.com/api-guide/) | Games & Comics | Reported; confirm access · Provider docs reviewed | Scalar candidate | 0 | Display a Yu-Gi-Oh! card name, attack value or card type. |
| 243 | [administrative-divisons-db](https://github.com/kamikazechaser/administrative-divisions-db) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from administrative-divisons-db. |
| 244 | [Airtel IP](https://aether.epias.ltd/ip2country/1.1.1.1/?full=true) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Airtel IP. |
| 245 | [BdAPIs](https://bdapis.com/) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from BdAPIs. |
| 246 | [bng2latlong](https://www.getthedata.com/bng2latlong) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from bng2latlong. |
| 247 | [Cartes.io](https://github.com/M-Media-Group/Cartes.io/wiki/API) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Cartes.io. |
| 248 | [Ducks Unlimited](https://gis.ducks.org/datasets/du-university-chapters/api) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Ducks Unlimited. |
| 249 | [France Administrative Geography API](https://geo.api.gouv.fr/) | Geocoding | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show a French commune name or population. |
| 250 | [FreeGeoIP](https://freegeoip.app/) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from FreeGeoIP. |
| 251 | [GeoApi](https://api.gouv.fr/api/geoapi.html) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from GeoApi. |
| 252 | [Geocode.xyz](https://geocode.xyz/) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Geocode.xyz. |
| 253 | [GeographQL](https://geographql.netlify.app) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from GeographQL. |
| 254 | [GeoJS](https://www.geojs.io/docs/v1/endpoints/geo/) | Geocoding | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Display the approximate region or timezone associated with an IP address. |
| 255 | [geoPlugin](https://www.geoplugin.com) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from geoPlugin. |
| 256 | [Graph Countries](https://github.com/lennertVanSever/graphcountries) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Graph Countries. |
| 257 | [IGN Geoplateforme Geocoding](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/geocodage/) | Geocoding | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Look up a French address or reverse-geocode coordinates into a short place name. |
| 258 | [Nominatim](https://nominatim.org/release-docs/latest/api/Overview/) | Geocoding | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Translate a place search or address into location metadata. |
| 259 | [Open Topo Data](https://www.opentopodata.org/) | Geocoding | Reported; confirm access · Provider docs reviewed | Scalar candidate | 0 | Show elevation at a selected coordinate. |
| 260 | [OpenPLZ API](https://www.openplzapi.org/) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a street, postal code or locality lookup result. |
| 261 | [Overpass API](https://overpass-api.de/) | Geocoding | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Count nearby mapped cafés, parks or other points of interest. |
| 262 | [Pinball Map](https://pinballmap.com/api/v1/docs) | Geocoding | Reported; confirm access · Directory discovery | Review required | 0 | Show a nearby pinball location or machine detail. |
| 263 | [Postcodes.io](https://postcodes.io/docs/overview/) | Geocoding | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Show the district, region or latitude of a UK postcode. |
| 264 | [ViaCEP](https://viacep.com.br/) | Geocoding | Reported; confirm access · Provider docs reviewed | Scalar candidate | 0 | Show the municipality or region for a Brazilian postcode. |
| 265 | [Zippopotam.us](https://www.zippopotam.us/) | Geocoding | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show a town, state or location for a postal code. |
| 266 | [Autobahn API](https://autobahn.api.bund.dev) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from Autobahn API. |
| 267 | [Ayes and Noes](https://ayesandnoes.co.uk/developers) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from Ayes and Noes. |
| 268 | [Bank Negara Malaysia Open Data](https://apikijangportal.bnm.gov.my/) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from Bank Negara Malaysia Open Data. |
| 269 | [Bidledger](https://jaydemks.github.io/bidledger/api.html) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from Bidledger. |
| 270 | [Brazil](https://brasilapi.com.br/) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from Brazil. |
| 271 | [Brazil Central Bank Open Data](https://dadosabertos.bcb.gov.br/) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Track a selected Brazilian economic reference series. |
| 272 | [Brazil CNPJ](https://cnpj.wiki/docs) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from Brazil CNPJ. |
| 273 | [Brazil Receita WS](https://www.receitaws.com.br/) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from Brazil Receita WS. |
| 274 | [Brazilian Chamber of Deputies Open Data](https://dadosabertos.camara.leg.br/swagger/api.html) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from Brazilian Chamber of Deputies Open Data. |
| 275 | [City, Bologna Opendata](https://dati.comune.bologna.it) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from City, Bologna Opendata. |
| 276 | [City, Gdańsk](https://ckan.multimediagdansk.pl/en) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from City, Gdańsk. |
| 277 | [City, Helsinki](https://hri.fi/en_gb/) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from City, Helsinki. |
| 278 | [Data USA](https://datausa.io/about/api/) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show a U.S. geography published population or economic statistic. |
| 279 | [FBI Wanted](https://www.fbi.gov/wanted/api) | Government | Reported; confirm access · Provider docs reviewed | Review required | 0 | Show public programme record totals or a missing-person notice category. |
| 280 | [Federal Register](https://www.federalregister.gov/reader-aids/developer-resources/rest-api) | Government | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Show document search totals or a published notice title. |
| 281 | [IBGE Data Service](https://servicodados.ibge.gov.br/api/docs/) | Government | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Display an administrative place name or published statistical indicator. |
| 282 | [Open Government, ACT](https://www.data.act.gov.au/) | Government | Reported; confirm access · Directory discovery | Review required | 0 | Show one public statistic or record from ACT. |
| 283 | [openFDA](https://open.fda.gov/apis/authentication/) | Government | Authentication unresolved · Provider docs reviewed | Review required | 0 | Count public recall notices or display a recall classification. |
| 284 | [Socrata Open Data](https://dev.socrata.com/docs/endpoints.html) | Government | Optional / mixed key scope · Provider docs reviewed | Review required | 0 | Show a city open-data count or aggregate statistic. |
| 285 | [UK Parliament Members API](https://members-api.parliament.uk/index.html) | Government | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show a public representative name or constituency. |
| 286 | [USAspending.gov](https://api.usaspending.gov/docs/) | Government | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Show published federal spending aggregates or award totals. |
| 287 | [DeepDNA](https://deepdna.ai/docs/) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from DeepDNA. |
| 288 | [FindSaunaPlunge](https://findsaunaplunge.com/api/) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short FindSaunaPlunge text item; check length and rendering before use. |
| 289 | [Healthcare.gov](https://www.healthcare.gov/developers/) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Show a public healthcare information title or short content item. |
| 290 | [Humanitarian Data Exchange](https://data.humdata.org/) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Show a public humanitarian dataset metadata or update date. |
| 291 | [ICD-10 Codes](https://clinicaltables.nlm.nih.gov/apidoc/icd10cm/v3/doc.html) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from ICD-10 Codes. |
| 292 | [Longevity World Cup](https://longevityworldcup.com/swagger) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from Longevity World Cup. |
| 293 | [MedlinePlus Genetics](https://medlineplus.gov/about/developers/geneticsdatafilesapi/) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Show a genetics topic or definition; XML requires parsing. |
| 294 | [MyVaccination](https://documenter.getpostman.com/view/16605343/Tzm8GG7u) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from MyVaccination. |
| 295 | [NPPES](https://npiregistry.cms.hhs.gov/registry/help-api) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Show a public U.S. healthcare-provider registry detail. |
| 296 | [Open Data NHS Scotland](https://www.opendata.nhs.scot) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected Scottish public-health statistic. |
| 297 | [Open Disease](https://disease.sh/) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from Open Disease. |
| 298 | [Urgences Québec](https://sante.handled.tools/en/donnees) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Track a reported Québec emergency-department occupancy value. |
| 299 | [Verified Supplement Data](https://verifiedsupplementdata.com/api/v1/recommend/index.json) | Health | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from Verified Supplement Data. |
| 300 | [AI Dev Jobs](https://aidevboard.com/api/v1/jobs) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected job-search result or listing count from AI Dev Jobs. |
| 301 | [Arbeitnow](https://documenter.getpostman.com/view/18545278/UVJbJdKh) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a current job listing title, location or listing count. |
| 302 | [Artificial Intelligence Jobs](https://artificialintelligencejobs.co/developers) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected job-search result or listing count from Artificial Intelligence Jobs. |
| 303 | [CuratorSearch](https://curatorsearch.com/developers) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected job-search result or listing count from CuratorSearch. |
| 304 | [DevITjobs](https://devitjobs.us/api/jobsLight) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected job-search result or listing count from DevITjobs. |
| 305 | [freehire](https://freehire.dev/docs/api) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected job-search result or listing count from freehire. |
| 306 | [Himalayas](https://himalayas.app/api) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a remote job, employer or location detail. |
| 307 | [Jobicy](https://jobicy.com/jobs-rss-feed) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a remote-job title, region or published timestamp. |
| 308 | [PayCrunch](https://paycrunch.co/api.html) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected job-search result or listing count from PayCrunch. |
| 309 | [RemoteOK](https://remoteok.com/api) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a remote vacancy title, tag or published timestamp. |
| 310 | [Search.gov Jobs](https://search.gov/developer/jobs.html) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected job-search result or listing count from Search.gov Jobs. |
| 311 | [TechRole Index](https://techrole.ru/open-data-daily) | Jobs | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected job-search result or listing count from TechRole Index. |
| 312 | [AI Economics Tools](https://piszczek.pl/tools/api) | Machine Learning | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact machine learning result from AI Economics Tools after choosing an appropriate endpoint. |
| 313 | [AI Model Watch](https://aimodelwatch.dev/api) | Machine Learning | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact machine learning result from AI Model Watch after choosing an appropriate endpoint. |
| 314 | [Modelfax](https://bytebrujo.github.io/modelfax/) | Machine Learning | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact machine learning result from Modelfax after choosing an appropriate endpoint. |
| 315 | [Statlyte](https://statlyte.com/api) | Machine Learning | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact machine learning result from Statlyte after choosing an appropriate endpoint. |
| 316 | [TensorFeed](https://tensorfeed.ai/developers) | Machine Learning | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact machine learning result from TensorFeed after choosing an appropriate endpoint. |
| 317 | [Gaana](https://github.com/cyberboysumanjay/GaanaAPI) | Music | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Gaana catalogue item or selected numeric detail. |
| 318 | [Genrenator](https://binaryjazz.us/genrenator-api/) | Music | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Genrenator catalogue item or selected numeric detail. |
| 319 | [JioSaavn](https://github.com/cyberboysumanjay/JioSaavnAPI) | Music | Reported; confirm access · Directory discovery | Review required | 0 | Show a short JioSaavn catalogue item or selected numeric detail. |
| 320 | [MusicBrainz](https://musicbrainz.org/doc/Development/XML_Web_Service/Version_2) | Music | Reported; confirm access · Directory discovery | Review required | 0 | Show an artist, release, recording or music catalogue detail. |
| 321 | [Openwhyd](https://openwhyd.github.io/openwhyd/API) | Music | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Openwhyd catalogue item or selected numeric detail. |
| 322 | [Radio Browser](https://api.radio-browser.info/) | Music | Reported; confirm access · Directory discovery | Review required | 0 | Discover a radio station and show its name, genre or country. |
| 323 | [SearchLy](https://www.github.com/AlbertSuarez/searchly) | Music | Reported; confirm access · Directory discovery | Review required | 0 | Show a short SearchLy catalogue item or selected numeric detail. |
| 324 | [Verome](https://github.com/Kirazul/Verome-API) | Music | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Verome catalogue item or selected numeric detail. |
| 325 | [DataCube AI](https://www.datacubeai.space/en/tools/ai-news-api) | News | Reported; confirm access · Directory discovery | Review required | 0 | Show a short headline, publication time or article-count result from DataCube AI. |
| 326 | [Florida Man](https://github.com/juliayxhuang/florida-man-api#readme) | News | Reported; confirm access · Directory discovery | Review required | 0 | Show a short headline, publication time or article-count result from Florida Man. |
| 327 | [Inshorts News](https://github.com/cyberboysumanjay/Inshorts-News-API) | News | Reported; confirm access · Directory discovery | Review required | 0 | Show a short headline, publication time or article-count result from Inshorts News. |
| 328 | [Noozra](https://noozra.com/api) | News | Reported; confirm access · Directory discovery | Review required | 0 | Show a short headline, publication time or article-count result from Noozra. |
| 329 | [OkSurf](https://ok.surf/) | News | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a OkSurf image or visual; this requires an image-capable widget. |
| 330 | [Spaceflight News](https://spaceflightnewsapi.net) | News | Reported; confirm access · Directory discovery | Review required | 0 | Show a short headline or publication timestamp about spaceflight. |
| 331 | [49 Gallery Historical Data](https://api.181649.com/docs) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open data result from 49 Gallery Historical Data after choosing an appropriate endpoint. |
| 332 | [Archive.org](https://archive.readme.io/docs) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Show a public archive item, metadata value or search count. |
| 333 | [BetTip](https://bettip.co.za/api/) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open data result from BetTip after choosing an appropriate endpoint. |
| 334 | [Big Data Explained](https://bigdataexplained.com/data) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open data result from Big Data Explained after choosing an appropriate endpoint. |
| 335 | [BotsArchive](https://botsarchive.com/docs.html) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open data result from BotsArchive after choosing an appropriate endpoint. |
| 336 | [BTU Graph](https://btugraph.com/data/) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open data result from BTU Graph after choosing an appropriate endpoint. |
| 337 | [Callook.info](https://callook.info) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Show a U.S. amateur-radio callsign lookup detail. |
| 338 | [CoworkingView](https://coworkingview.com/en/api) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open data result from CoworkingView after choosing an appropriate endpoint. |
| 339 | [CuttingToolsAI](https://cuttingtoolsai.eu/api) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open data result from CuttingToolsAI after choosing an appropriate endpoint. |
| 340 | [DevLifeCheck](https://devlifecheck.com/developers) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open data result from DevLifeCheck after choosing an appropriate endpoint. |
| 341 | [EOSL](https://eosl.ai/api/) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open data result from EOSL after choosing an appropriate endpoint. |
| 342 | [HousingFeed](https://housingfeed.com/docs) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open data result from HousingFeed after choosing an appropriate endpoint. |
| 343 | [i6eal Open AI Data](https://i6eal.de/en/tools/data/) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open data result from i6eal Open AI Data after choosing an appropriate endpoint. |
| 344 | [Universities List](https://github.com/Hipo/university-domains-list) | Open Data | Reported; confirm access · Directory discovery | Review required | 0 | Show a university name, country or domain. |
| 345 | [Drupal.org](https://www.drupal.org/drupalorg/docs/api) | Open Source Projects | Reported; confirm access · Directory discovery | Review required | 0 | Show a public project release or development statistic. |
| 346 | [GitHub Contribution Chart Generator](https://github-contributions.vercel.app) | Open Source Projects | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a GitHub Contribution Chart Generator image or visual; this requires an image-capable widget. |
| 347 | [GitHub ReadMe Stats](https://github.com/anuraghazra/github-readme-stats) | Open Source Projects | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open source projects result from GitHub ReadMe Stats after choosing an appropriate endpoint. |
| 348 | [Neuronto ARD Registry](https://neuronto.com/api-docs) | Open Source Projects | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact open source projects result from Neuronto ARD Registry after choosing an appropriate endpoint. |
| 349 | [Shields](https://shields.io/) | Open Source Projects | Reported; confirm access · Directory discovery | Review required | 0 | Show a project badge value; SVG output requires a different widget. |
| 350 | [USPTO](https://www.uspto.gov/learning-and-resources/open-data-and-mobility) | Patent | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact patent result from USPTO after choosing an appropriate endpoint. |
| 351 | [chucknorris.io](https://api.chucknorris.io) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short chucknorris.io text item; check length and rendering before use. |
| 352 | [Deckaura Horoscope](https://horoscope.deckaura.com) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact personality result from Deckaura Horoscope after choosing an appropriate endpoint. |
| 353 | [Dictum](https://github.com/fisenkodv/dictum) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact personality result from Dictum after choosing an appropriate endpoint. |
| 354 | [Echoes](https://echoes.soferity.com) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Echoes text item; check length and rendering before use. |
| 355 | [icanhazdadjoke](https://icanhazdadjoke.com/api) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short icanhazdadjoke text item; check length and rendering before use. |
| 356 | [kanye.rest](https://kanye.rest) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short kanye.rest text item; check length and rendering before use. |
| 357 | [Meme](https://github.com/D3vd/Meme_Api) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact personality result from Meme after choosing an appropriate endpoint. |
| 358 | [Memesio](https://memesio.com/developers/api) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact personality result from Memesio after choosing an appropriate endpoint. |
| 359 | [NaMoMemes](https://github.com/theIYD/NaMoMemes) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact personality result from NaMoMemes after choosing an appropriate endpoint. |
| 360 | [Perchance as a Service](https://perchance.synopsys0.workers.dev) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact personality result from Perchance as a Service after choosing an appropriate endpoint. |
| 361 | [Personality.fyi](https://personality.fyi/api) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact personality result from Personality.fyi after choosing an appropriate endpoint. |
| 362 | [PositiveQuotation](https://positivequotation.com/developers/public-domain-quotes-api) | Personality | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact personality result from PositiveQuotation after choosing an appropriate endpoint. |
| 363 | [Phone Specification](https://github.com/azharimm/phone-specs-api) | Phone | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact phone result from Phone Specification after choosing an appropriate endpoint. |
| 364 | [Kavel](https://kavel.readthedocs.io/) | Photography | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a Kavel image or visual; this requires an image-capable widget. |
| 365 | [Lorem Picsum](https://picsum.photos/) | Photography | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a Lorem Picsum image or visual; this requires an image-capable widget. |
| 366 | [PlaceKeanu](https://placekeanu.com/) | Photography | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a PlaceKeanu image or visual; this requires an image-capable widget. |
| 367 | [Readme typing SVG](https://github.com/DenverCoder1/readme-typing-svg) | Photography | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a Readme typing SVG image or visual; this requires an image-capable widget. |
| 368 | [Screenshot Studio](https://www.screenshot-studio.com/docs) | Photography | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a Screenshot Studio image or visual; this requires an image-capable widget. |
| 369 | [arcsecond.io](https://api.arcsecond.io/) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from arcsecond.io. |
| 370 | [Botlero](https://botlero.com/api/robots) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Botlero text item; check length and rendering before use. |
| 371 | [ClinicalTrials.gov](https://clinicaltrials.gov/data-api/api) | Science & Math | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Count public studies for a topic or show a trial recruitment status. |
| 372 | [CodeCogs](https://editor.codecogs.com/docs/4-LaTeX_rendering.php) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a CodeCogs image or visual; this requires an image-capable widget. |
| 373 | [CycleCalcs](https://www.cyclecalcs.com/api.html) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from CycleCalcs. |
| 374 | [DataCite](https://support.datacite.org/docs/api) | Science & Math | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Display a dataset title, publication year or search result count. |
| 375 | [Ensembl REST](https://rest.ensembl.org/) | Science & Math | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Display a gene label, genome build or service release. |
| 376 | [Europe PMC](https://europepmc.org/RestfulWebService) | Science & Math | Reported; confirm access · Provider docs reviewed | Scalar candidate | 0 | Count papers matching a research interest or display a citation count. |
| 377 | [Figshare](https://docs.figshare.com/v2/) | Science & Math | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show a research dataset title or published item count. |
| 378 | [GBIF](https://techdocs.gbif.org/en/openapi/) | Science & Math | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show the number of biodiversity observations recorded for a country or species. |
| 379 | [iDigBio](https://github.com/idigbio/idigbio-search-api/wiki) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Show a specimen, taxon or biodiversity search detail. |
| 380 | [iNaturalist](https://www.inaturalist.org/pages/api+reference) | Science & Math | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Track local wildlife observation totals or a chosen species. |
| 381 | [inspirehep.net](https://github.com/inspirehep/rest-api-doc) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Show a high-energy-physics paper, author or citation result. |
| 382 | [isEven (humor)](https://isevenapi.xyz/) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from isEven (humor). |
| 383 | [ISRO](https://isro.vercel.app) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from ISRO. |
| 384 | [ITIS](https://www.itis.gov/ws_description.html) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Show a species scientific name or taxonomic classification. |
| 385 | [MyGene.info](https://docs.mygene.info/en/latest/doc/query_service.html) | Science & Math | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show a gene symbol or the number of matching gene records. |
| 386 | [Newton](https://newton.now.sh/) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from Newton. |
| 387 | [Noctua](https://api.noctuasky.com/api/v1/swaggerdoc/) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from Noctua. |
| 388 | [Open Science Framework](https://developer.osf.io/) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Display public research project metadata or publication activity. |
| 389 | [OpenAlex](https://help.openalex.org/api/authentication/) | Science & Math | Optional / mixed key scope · Provider docs reviewed | Review required | 0 | Track publication counts or citations for an author or topic. |
| 390 | [PubChem PUG REST](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest) | Science & Math | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Display a molecular mass or simple property of a chosen compound. |
| 391 | [RCSB Protein Data Bank](https://www.rcsb.org/docs/programmatic-access/web-apis-overview) | Science & Math | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show a selected protein structure title, resolution or release date. |
| 392 | [Unpaywall](https://unpaywall.org/products/api) | Science & Math | Reported; confirm access · Directory discovery | Review required | 0 | Show open-access availability for a paper; contact-email requirements need review. |
| 393 | [Agent Verifier](https://packet.guru/agents/reference) | Security | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact security result from Agent Verifier after choosing an appropriate endpoint. |
| 394 | [Blooms](https://blooms-production.up.railway.app/api) | Security | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact security result from Blooms after choosing an appropriate endpoint. |
| 395 | [CSR.plus](https://csr.plus/docs/api) | Security | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact security result from CSR.plus after choosing an appropriate endpoint. |
| 396 | [CVE.report](https://cve.report/api) | Security | Reported; confirm access · Directory discovery | Review required | 0 | Show a vulnerability identifier or advisory detail. |
| 397 | [Microsoft Security Response Center (MSRC)](https://msrc.microsoft.com/report/developer) | Security | Reported; confirm access · Directory discovery | Review required | 0 | Show a public security-update date or vulnerability metadata. |
| 398 | [SSL Labs](https://github.com/ssllabs/ssllabs-scan/blob/master/ssllabs-api-docs-v3.md) | Security | Reported; confirm access · Directory discovery | Review required | 0 | Show a public TLS assessment grade; avoid repeatedly initiating scans. |
| 399 | [UK Police](https://data.police.uk/docs/) | Security | Reported; confirm access · Directory discovery | Review required | 0 | Show a public local-crime count or neighbourhood detail. |
| 400 | [BirkinBagStock](https://birkinbagstock.com/.well-known/openapi.json) | Shopping | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact shopping result from BirkinBagStock after choosing an appropriate endpoint. |
| 401 | [Folderwijzer Folders](https://folderwijzer.nl/folder-api/) | Shopping | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact shopping result from Folderwijzer Folders after choosing an appropriate endpoint. |
| 402 | [Marketplace Fee Data](https://www.sellerscalc.com/data) | Shopping | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact shopping result from Marketplace Fee Data after choosing an appropriate endpoint. |
| 403 | [OneFindMe](https://onefindme.com/mcp) | Shopping | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact shopping result from OneFindMe after choosing an appropriate endpoint. |
| 404 | [Profitvana](https://www.profitvana.com/developers) | Shopping | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact shopping result from Profitvana after choosing an appropriate endpoint. |
| 405 | [4chan](https://github.com/4chan/4chan-API) | Social | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a 4chan image or visual; this requires an image-capable widget. |
| 406 | [HackerNews](https://github.com/HackerNews/API) | Social | Reported; confirm access · Directory discovery | Review required | 0 | Show a short top-story title, score or comment count. |
| 407 | [Hashnode](https://hashnode.com) | Social | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact social result from Hashnode after choosing an appropriate endpoint. |
| 408 | [Lanyard](https://github.com/Phineas/lanyard) | Social | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact social result from Lanyard after choosing an appropriate endpoint. |
| 409 | [Open Collective](https://docs.opencollective.com/help/developers/api) | Social | Reported; confirm access · Directory discovery | Review required | 0 | Show a public collective contribution or funding statistic; GraphQL needs an adapter. |
| 410 | [SwarmMemo](https://swarmmemo.com/protocol.md) | Social | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact social result from SwarmMemo after choosing an appropriate endpoint. |
| 411 | [CelesTrak GP Data](https://celestrak.org/NORAD/documentation/gp-data-formats.php) | Space & Astronomy | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Public satellite orbital element data |
| 412 | [JPL SSD API Suite](https://ssd-api.jpl.nasa.gov/doc/) | Space & Astronomy | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Asteroids, close approaches and orbital calculations |
| 413 | [Launch Library 2](https://thespacedevs.com/llapi) | Space & Astronomy | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Upcoming rocket launches and space events |
| 414 | [NOAA SWPC Product Data](https://www.spaceweather.gov/products) | Space & Astronomy | Documented public scope · Provider docs reviewed | Scalar candidate | 6 | Solar, geomagnetic and radio blackout scales |
| 415 | [Sunrise-Sunset.org API](https://sunrise-sunset.org/api) | Space & Astronomy | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Sunrise, sunset and daylight times |
| 416 | [SunriseSunset.io API](https://sunrisesunset.io/api/) | Space & Astronomy | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Sun and moon times for a selected location |
| 417 | [TLE API](https://tle.ivanstanojevic.me/) | Space & Astronomy | Reported; confirm access · Provider docs reviewed | Review required | 0 | Read satellite orbital element metadata. |
| 418 | [Where the ISS at?](https://wheretheiss.at/w/developer) | Space & Astronomy | Documented public scope · Provider docs reviewed | Scalar candidate | 3 | ISS position, altitude and velocity |
| 419 | [Bet Better](https://betbetter.world/api/) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected fixture, result or published sport statistic from Bet Better. |
| 420 | [Cartola FC](https://github.com/wgenial/cartrolandofc) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected fixture, result or published sport statistic from Cartola FC. |
| 421 | [City Bikes](https://api.citybik.es/v2/) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Track available bicycles or docks at a chosen station. |
| 422 | [F1 API](https://f1api.dev) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected fixture, result or published sport statistic from F1 API. |
| 423 | [F1 Data API](https://github.com/Jacobbrewer1/f1-data) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected fixture, result or published sport statistic from F1 Data API. |
| 424 | [FanLine Wire](https://fanlinewire.com/docs) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected fixture, result or published sport statistic from FanLine Wire. |
| 425 | [Football (Soccer) Videos](https://www.scorebat.com/video-api/) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected fixture, result or published sport statistic from Football (Soccer) Videos. |
| 426 | [Football Standings](https://github.com/azharimm/football-standings-api) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected fixture, result or published sport statistic from Football Standings. |
| 427 | [Golf-Data](https://github.com/Jacobbrewer1/golf-data-docs) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected fixture, result or published sport statistic from Golf-Data. |
| 428 | [MoviOdds](https://moviodds.com/doc) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected fixture, result or published sport statistic from MoviOdds. |
| 429 | [NHL Records and Stats](https://gitlab.com/dword4/nhlapi) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected hockey team, player or game statistic. |
| 430 | [OpenF1](https://openf1.org/) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show an F1 meeting, driver or session telemetry value. |
| 431 | [OpenLigaDB](https://www.openligadb.de) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show a team result, match status or score. |
| 432 | [Squiggle](https://api.squiggle.com.au) | Sports & Fitness | Reported; confirm access · Directory discovery | Review required | 0 | Show an Australian football result or forecast statistic. |
| 433 | [AddressMock](https://addressmock.com/api) | Test Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact test data result from AddressMock after choosing an appropriate endpoint. |
| 434 | [Bacon Ipsum](https://baconipsum.com/json-api/) | Test Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact test data result from Bacon Ipsum after choosing an appropriate endpoint. |
| 435 | [Dicebear Avatars](https://avatars.dicebear.com/) | Test Data | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a Dicebear Avatars image or visual; this requires an image-capable widget. |
| 436 | [DummyJSON](https://dummyjson.com/) | Test Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact test data result from DummyJSON after choosing an appropriate endpoint. |
| 437 | [FakeNamely](https://fakenamely.com/api) | Test Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact test data result from FakeNamely after choosing an appropriate endpoint. |
| 438 | [flaky](https://flakyapi.dev) | Test Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact test data result from flaky after choosing an appropriate endpoint. |
| 439 | [ItsThisForThat](https://itsthisforthat.com/api.php) | Test Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact test data result from ItsThisForThat after choosing an appropriate endpoint. |
| 440 | [JSONing](https://jsoning.com/api/) | Test Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact test data result from JSONing after choosing an appropriate endpoint. |
| 441 | [loremfile](https://loremfile.dev/docs/manifest) | Test Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact test data result from loremfile after choosing an appropriate endpoint. |
| 442 | [TotalShiftLeft Sandbox](https://demo.totalshiftleft.ai/) | Test Data | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact test data result from TotalShiftLeft Sandbox after choosing an appropriate endpoint. |
| 443 | [Gawrshdarn](https://api.gawrshdarn.com) | Text Analysis | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact text analysis result from Gawrshdarn after choosing an appropriate endpoint. |
| 444 | [Yomi](https://github.com/ookii-tsuki/yomi) | Text Analysis | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact text analysis result from Yomi after choosing an appropriate endpoint. |
| 445 | [WhatPulse](https://developer.whatpulse.org/#web-api) | Tracking | Reported; confirm access · Directory discovery | Review required | 0 | Explore a compact tracking result from WhatPulse after choosing an appropriate endpoint. |
| 446 | [Aero Key, India](https://aerokey-api.vercel.app/) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Aero Key, India. |
| 447 | [airportsapi](https://airport-web.appspot.com/api/docs/) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from airportsapi. |
| 448 | [ArcNautical](https://arcnautical.com/developers/) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from ArcNautical. |
| 449 | [Aviation Safety Data](https://himaxym.com/developers) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Aviation Safety Data. |
| 450 | [BC Ferries](https://www.bcferriesapi.ca) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected sailing time or reported capacity. |
| 451 | [Can I enter](https://canienter.com) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Can I enter. |
| 452 | [ChargeAlong](https://chargealong.io/docs/) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from ChargeAlong. |
| 453 | [Deutsche Bahn transport.rest](https://v6.db.transport.rest/api.html) | Transportation | Reported; confirm access · Provider docs reviewed | Scalar candidate | 3 | Show a German rail departure, delay or service destination. |
| 454 | [Entur](https://developer.entur.no/) | Transportation | Reported; confirm access · Provider docs reviewed | Adapter / policy work | 0 | Show a Norwegian public-transport departure or disruption. |
| 455 | [iRail](https://docs.irail.be/) | Transportation | Reported; confirm access · Provider docs reviewed | Scalar candidate | 0 | Show a Belgian rail departure, platform or delay. |
| 456 | [MBTA V3](https://api-v3.mbta.com/docs/swagger/index.html) | Transportation | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show a Boston transit prediction, route label or alert. |
| 457 | [OpenSky Network](https://openskynetwork.github.io/opensky-api/rest.html) | Transportation | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Show a selected aircraft state or flight activity for a small area. |
| 458 | [REFUGE Restrooms](https://www.refugerestrooms.org/api/docs/#!/restrooms) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected restroom location or accessibility detail. |
| 459 | [Swiss Public Transport](https://transport.opendata.ch/docs.html) | Transportation | Reported; confirm access · Provider docs reviewed | Scalar candidate | 0 | Show a Swiss station departure or connection time. |
| 460 | [Transport for Auckland, New Zealand](https://dev-portal.at.govt.nz/) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Transport for Auckland, New Zealand. |
| 461 | [Transport for Czech Republic](https://www.chaps.cz/eng/products/idos-internet) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Transport for Czech Republic. |
| 462 | [Transport for London Unified API](https://api-portal.tfl.gov.uk/) | Transportation | Documented public scope · Provider docs reviewed | Scalar candidate | 1 | Show London line status or a stop arrival prediction. |
| 463 | [Transport for Los Angeles, US](https://developer.metro.net/api/) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Transport for Los Angeles, US. |
| 464 | [Transport for Spain](https://data.renfe.com/api/1/util/snippet/api_info.html?resource_id=a2368cff-1562-4dde-8466-9635ea3a572a) | Transportation | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Transport for Spain. |
| 465 | [Bike Reliability](https://bikereliability.co.uk/developers) | Vehicle | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Bike Reliability. |
| 466 | [Brazilian Vehicles and Prices](https://deividfortuna.github.io/fipe/) | Vehicle | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from Brazilian Vehicles and Prices. |
| 467 | [NHTSA](https://vpic.nhtsa.dot.gov/api/) | Vehicle | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected vehicle-model, recall or VIN-decoding detail. |
| 468 | [ProblemsByVin](https://problemsbyvin.com/data/) | Vehicle | Reported; confirm access · Directory discovery | Review required | 0 | Show a selected location, journey or vehicle detail from ProblemsByVin. |
| 469 | [Window Sticker](https://windowsticker.org/api-docs) | Vehicle | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Window Sticker text item; check length and rendering before use. |
| 470 | [An API of Ice And Fire](https://anapioficeandfire.com/) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Show a fantasy character, house or book detail. |
| 471 | [Bob's Burgers API](https://bobsburgersapi.com/) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a Bob's Burgers API image or visual; this requires an image-capable widget. |
| 472 | [Dune](https://github.com/ywalia01/dune-api) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Dune catalogue item or selected numeric detail. |
| 473 | [Final Space](https://finalspaceapi.com/docs/) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Final Space catalogue item or selected numeric detail. |
| 474 | [Game of Thrones Quotes](https://gameofthronesquotes.xyz/) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Game of Thrones Quotes text item; check length and rendering before use. |
| 475 | [Lucifer Quotes](https://github.com/shadowoff09/lucifer-quotes) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Lucifer Quotes text item; check length and rendering before use. |
| 476 | [MCU Countdown](https://github.com/DiljotSG/MCU-Countdown) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Show a short MCU Countdown catalogue item or selected numeric detail. |
| 477 | [Movie Quote](https://github.com/F4R4N/movie-quote/) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Movie Quote text item; check length and rendering before use. |
| 478 | [Owen Wilson Wow](https://owen-wilson-wow-api.onrender.com/) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Owen Wilson Wow catalogue item or selected numeric detail. |
| 479 | [Potter DB](https://potterdb.com) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Show a Harry Potter character, book or film detail. |
| 480 | [Ron Swanson Quotes](https://github.com/jamesseanwright/ron-swanson-quotes#ron-swanson-quotes-api) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Ron Swanson Quotes catalogue item or selected numeric detail. |
| 481 | [Shoof Aflam](https://shoofaflam.tv/api-docs/) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Show a short Shoof Aflam catalogue item or selected numeric detail. |
| 482 | [Shrek Quotes](https://shrekofficial.com) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Rotate a short Shrek Quotes text item; check length and rendering before use. |
| 483 | [STAPI](https://stapi.co) | Video | Reported; confirm access · Directory discovery | Review required | 0 | Show a Star Trek character, episode or catalogue statistic. |
| 484 | [AviationWeather](https://aviationweather.gov/data/api/) | Weather | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Show a nearby airport METAR observation or flight-weather advisory. |
| 485 | [DWD API](https://dwd.api.bund.dev/) | Weather | Reported; confirm access · Directory discovery | Review required | 0 | Track a German station observation or weather warning. |
| 486 | [FMI Open Data WFS](https://en.ilmatieteenlaitos.fi/open-data-manual-fmi-wfs-services) | Weather | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Finnish observations and forecasts |
| 487 | [Hong Kong Obervatory](https://www.hko.gov.hk/en/abouthko/opendata_intro.htm) | Weather | Reported; confirm access · Directory discovery | Review required | 0 | Show the current Hong Kong weather or an official warning. |
| 488 | [IPMA Open Data API](https://api.ipma.pt/) | Weather | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Portugal forecasts and environmental observations |
| 489 | [MET Norway Weather API](https://api.met.no/doc/TermsOfService) | Weather | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | Location forecasts and astronomical data |
| 490 | [Meteo.lt API](https://api.meteo.lt/) | Weather | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Lithuanian weather and hydrological observations |
| 491 | [MSC GeoMet API](https://eccc-msc.github.io/open-data/msc-geomet/readme_en/) | Weather | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Canadian meteorological/geospatial observations |
| 492 | [NASA POWER API](https://power.larc.nasa.gov/docs/services/api/) | Weather | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Solar irradiance and meteorological historical data |
| 493 | [NOAA CO-OPS Data API](https://api.tidesandcurrents.noaa.gov/api/prod/) | Weather | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Tide levels, tide predictions and coastal conditions |
| 494 | [NWS Weather API](https://www.weather.gov/documentation/services-web-api) | Weather | Documented public scope · Provider docs reviewed | Adapter / policy work | 0 | US weather forecast and observation |
| 495 | [Open-Meteo](https://open-meteo.com/en/docs) | Weather | Documented public scope · Provider docs reviewed | Scalar candidate | 24 | Local weather, air quality and forecast readings |
| 496 | [RainViewer](https://www.rainviewer.com/api.html) | Weather | Reported; confirm access · Directory discovery | Review required | 0 | Track rain-radar availability or timestamp; maps need a richer widget. |
| 497 | [Terrace Weather](https://terrace.javiermateo.dev/swagger-ui.html) | Weather | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from Terrace Weather. |
| 498 | [WeatherTotals](https://weathertotals.com/api) | Weather | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from WeatherTotals. |
| 499 | [World Time & Weather](https://worldtimeweather.com/api.html) | Weather | Reported; confirm access · Directory discovery | Review required | 0 | Show one public observation or documented reference value from World Time & Weather. |
| 500 | [wttr.in](https://github.com/chubin/wttr.in) | Weather | Documented public scope · Provider docs reviewed | Scalar candidate | 0 | Human-readable local weather with JSON option |

## Source and licence provenance

Discovery used the community [public-apis/public-apis](https://github.com/public-apis/public-apis) and [public-api-lists/public-api-lists](https://github.com/public-api-lists/public-api-lists) directories, followed by provider-owned documentation where reviewed. The catalogue contains original short desk-use descriptions and explicit evidence classifications.

The directory MIT notices are included as [public-apis-MIT.txt](../third_party/catalog-discovery/public-apis-MIT.txt) and [public-api-lists-MIT.txt](../third_party/catalog-discovery/public-api-lists-MIT.txt), with snapshot and licence hashes in [PROVENANCE.json](../third_party/catalog-discovery/PROVENANCE.json). These licences apply to discovery metadata; they do not grant rights to provider data or services.

The public generator reads only public JSON and licence files. It recreates the adjacent C++ string literal containing `API_SERVICES` and `SERVICE_READINGS`; private research snapshots, raw API responses, device identifiers and saved user configuration are not required for a build.

```sh
python3 tools/generate_api_services.py --check
python3 tools/test_api_services.py
```
