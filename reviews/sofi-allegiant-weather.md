# SoFi and Allegiant weather integration

September 11, 2026 UTC: the conservative OSM candidate collector found one exact named stadium feature for SoFi and Allegiant. Each feature's street number, street, municipality and state reconcile with the official address already retained in `data/weather-venues.json`. Their derived bounding-box midpoints resolve through NWS to California LOX/151,41 and Nevada VEF/121,95. NWS's nearest locality for Allegiant is Paradise; the official and OSM mailing addresses both use Las Vegas. This locality label is not used to rewrite the address.

The accepted candidate records are preserved in `sofi-allegiant-location-candidates.json`, with full compressed OSM and NWS response bytes in `data/weather-location-sources`. Attribution and ODbL links remain in the public weather panel. The separate Census records still accurately show that the Census lookup returned no match; the OSM registry supplies the independently verified alternative.

The real weather refresh now provides twelve game records across 23 verified US venue locations. The two new games are Cardinals–Chargers (`2026_01_ARI_LAC`) and Dolphins–Raiders (`2026_01_MIA_LV`). Outdoor area forecasts do not establish field-level conditions or roof operation and do not change the numerical forecast. Existing SoFi roof context remains separate.

Sixteen related Python tests passed, including reproduction of retained OSM/NWS bytes and exact coordinate/address checks. Chromium and WebKit at 320px passed on both games: actual forecast, correct NWS source link, visible OSM attribution and no document overflow or page errors. See `sofi-allegiant-weather-browser.json`.

The production build passed. Independent review verified registry/candidate identity, retained source hashes, coordinates, active-game bindings and preservation of prior ledger entries; no issue was found.

U.S. Bank Stadium did not produce exactly one named map feature and remains unavailable. No alternate-name match was silently promoted. This is staged development evidence, not a public publication receipt.
