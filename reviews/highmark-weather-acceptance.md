# Highmark 2026 stadium-area weather acceptance

The location now uses a reviewed geographic reconciliation rather than postal
address matching. The Bills' official stadium page links map 2167. Its actual
Entry 1 location (1203446, category 107420) lies within retained OSM way 1339149058,
tagged as a football stadium opening in 2026. The derived bounds midpoint is
42.77304225, -78.79219105. NWS returned the requested rounded point in New York
and the corresponding Buffalo forecast grid.

`official_map_evidence.py` verifies the full retained source chain, identifiers,
named location, bounds/containment, midpoint, NWS point/grid and registry bindings.
Category placeholders at 0,0 cannot qualify. The One versus 10 Bills Plaza house
number remains unresolved and is disclosed in the source explanation. This is
an area-weather lookup, not surveyed field coordinates or proof of roof status.
The map is unavailable to pre-2026 or missing-season requests.

The current Overpass request timed out; the verified September 10 geometry was
reused with its original retrieval time and exact hash, rather than relabeled
as new. The named-entrance response, official page and NWS point were acquired
for this review. No map imagery is redistributed in the product.

An initial timing assumption was corrected against the actual schedule:
Detroit–Buffalo kicks off September 18 at 00:15 UTC, within the seven-day window
at this check. Real acquisition succeeded. The refresh now contains 14 available
game forecasts and 137 retained observations, all independently replayed against
source bytes. Venue coverage increases to 25. Numerical forecasts, the canonical
model ledger and frozen model/research files are unchanged.

Independent source review found no material acceptance defect. Four new evidence
tests (with tampering/identity cases), seven acquisition tests, ten existing venue
tests and four history tests passed. TypeScript checking and the production build
passed. The actual pending-forecast Detroit–Buffalo page passed six Chromium/WebKit
checks at 320, 390 and 1280px, including source disclosure, no horizontal overflow
and no automated WCAG A/AA violations in the weather panel. The 390px screenshot
was visually inspected. This verifies local coverage, not public deployment or
future forecast accuracy.
