# Current-slate weather expansion — September 10, 2026

Added EverBank Stadium and MetLife Stadium after matching their named OSM stadium bounds to the recorded official house number, street, city, and state. NWS returned hourly forecast endpoints for Jacksonville, FL and East Rutherford, NJ, respectively. The raw map response, exact point responses and source fingerprints are archived. OSM attribution and ODbL terms follow the previous map expansion.

The live-data refresh now produces seven eligible forecasts, adding Browns–Jaguars and Cowboys–Giants. Total configured locations increase from fourteen to sixteen. Acrisure Stadium remains withheld because its map object has no address tags; a matching stadium name alone does not satisfy the current reconciliation rule.

`scripts/acquire_venue_maps.py` reproduces the acquisition process. It accepts unique names already backed by recorded official addresses, uses a bounded exact-name query, rejects provider timeout remarks, checks each candidate against the address/geometry contract, and writes a review candidate report. It never changes the production venue map. The two accepted candidates were inspected before publication. Invalid names and duplicate requests fail before network access. This is a one-off source acquisition tool, not an additional scheduled API dependency.

Validation: two acquisition tests, five venue-evidence tests and seven weather tests pass, as does the production build. All accepted map and point bytes reproduce their recorded hashes, and the point coordinates match the derived lookup requests. Existing numerical forecasts are unchanged.
