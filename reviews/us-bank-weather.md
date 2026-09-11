# U.S. Bank Stadium location reconciliation

The initial exact-name OSM lookup returned no object. A bounded Minneapolis discovery query found `US Bank Stadium`, way 743461508, with the exact official address: 401 Chicago Avenue, Minneapolis, MN 55415. It also found Huntington Bank Stadium at a different address; that object was not selected. Discovery response SHA-256: `bcba2fee23d70a35a606ce3796190b092fb1a8aa20d46571b54cabdec88ec1af`, retained in `data/weather-location-sources`.

The collector now has one reviewed exact spelling mapping from `U.S. Bank Stadium` to `US Bank Stadium`. It does not remove punctuation generally or permit fuzzy names. The same unique-object, official-address, bounds, state and NWS checks still apply. A regression verifies unrelated names and other spellings remain unchanged. The new exact query and accepted candidate are retained in `us-bank-location-candidate.json`, including source hashes and coordinates.

The real collector produced kickoff-hour context for Packers–Vikings (`2026_01_GB_MIN`). Local coverage is now thirteen available games across 24 verified US locations. Outdoor area forecasts do not establish indoor/field conditions or change numerical predictions. Census's original no-match record remains intact; the map record provides the separately verified alternative.

Seventeen venue/acquisition/weather tests passed. Chromium and WebKit at 320px displayed the actual forecast, correct NWS link and OSM attribution with no page errors or overflow. Evidence is in `us-bank-weather-browser.json`. Prior ledger records remain preserved. This is local evidence, not public deployment or full launch acceptance.
