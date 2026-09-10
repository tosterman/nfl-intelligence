# Smaller homepage revision payload

Home now prepares validated weekly briefing views on the server for every available week. The client receives summary fields and unavailable-history identifiers instead of full revision histories for all games. The slate retains current forecasts, the full schedule and dynamic filter/navigation state. Canonical histories are unchanged and remain accessible through matchup links.

A regression test compares complete rendered briefing markup before and after projection, including a missing-current-forecast history and return URL; it verifies nonmutation and omission of full histories/predictions from the summary. All seven weekly-change tests pass. Chromium and WebKit verified slate search/filter/sort to matchup history and back. Independent source review found no semantic or week-navigation regression. The production build passed.

Local production HTML measurements: decoded homepage bytes fell from 882,229 to 435,919; compressed bytes from 53,912 to 35,430. Compare `local-page-weight.json` with `homepage-weight-after.json`. These single local observations measure document size, not representative user latency or total network cost. Both measurements returned 200 with no browser page errors. The temporary production server was stopped after measurement. Nothing was deployed.
