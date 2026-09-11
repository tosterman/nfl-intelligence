# Ford Field weather coverage

Verified September 11, 2026 UTC. Ford Field's official address page identifies 2000 Brush Street, Detroit, MI 48226: https://www.fordfield.com/stadium-info/about-ford-field . The Census geocoder returned one matching street/locality/state record, accepted by the existing strict venue validator. Coordinates are an address-interpolated vicinity point, not surveyed field coordinates.

The complete Census response is retained in `data/weather-location-sources/213a296c22c863feb93ff3a2b20ef2ef3b7b3eafc68597d6dc22cb0729e66ebc.json.gz`. The registry records its raw-byte hash, source URL, acquisition time and returned match. NWS points lookup resolves to Michigan grid DTX/66,34. The real weather collector then produced the kickoff-hour record for `2026_01_NO_DET`, preserving NWS response bytes and appending the weather ledger.

The local refresh has nine available games and the registry now covers 20 US locations. Later Ford Field games outside the seven-day window remain unavailable. Numerical forecasts were not changed. This adds outdoor area context; it makes no assertion about indoor temperature, roof state or on-field wind.

Seven weather tests and six venue-evidence tests passed. Chromium and WebKit at 320px displayed the actual temperature, matching NWS source link and expanded outdoor-area limitation with no page errors or document overflow. The initial browser assertion incorrectly expected a Census label in the rendered panel; inspection showed the existing display uses the area limitation and NWS attribution, so verification was corrected to those actual contracts. Evidence: `ford-field-weather-browser.json`.

This is local development evidence, not a public deployment receipt.
