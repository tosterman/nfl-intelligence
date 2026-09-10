# Levi’s Stadium weather location

The operator’s [contact page](https://levisstadium.com/contact-us/), checked September 10, 2026, lists 4900 Marie P. DeBartolo Way, Santa Clara, CA 95054. Census returned no match; that response remains retained and was not promoted to a coordinate.

[OSM way 296503400](https://www.openstreetmap.org/way/296503400) has the same house number, street, city and state, together with the operator website. Its recorded bounding-box midpoint is 37.4029927, -121.9700565. NWS resolves the rounded lookup point to Santa Clara, California, with the MTR/97,86 hourly endpoint. This is an area forecast lookup, not a surveyed field coordinate. OSM attribution and ODbL terms remain attached to the location record and user-visible weather source details.

The original exact-name query failed because the OSM name uses a curly apostrophe while the schedule uses a straight one. The acquisition tool now queries both typographic forms and normalizes only U+2019 to an ASCII apostrophe for name comparison. It still requires exactly one stadium result and exact address/geometry reconciliation; it does not remove words or accept fuzzy names. Repeating the acquisition with the updated tool returned one validated candidate. Raw Census, OSM and NWS responses are retained under their SHA-256 identities.

Configured verified locations increase from 17 to 18. This adds future Santa Clara coverage when games enter the seven-day collection window; it does not add a current kickoff-hour forecast or cover the 49ers’ neutral-site Melbourne game. No numerical prediction changes. International coverage, Pittsburgh location reconciliation, and roof-status evidence remain unfinished. During this review the schedule’s Melbourne roof field was observed as `dome`; the existing weather collector already withholds neutral-site coverage and does not use that field. It has not been promoted to a verified physical-venue fact.

Validation: six venue-evidence tests, two acquisition tests and seven weather tests pass. All accepted map/point source bytes and their derived coordinates are verified by the venue tests. TypeScript checking passes. Production rollout remains pending.

Independent source review verified archived hashes, the exact map element, official-address consistency, derived midpoint and NWS endpoint, with no blocker found. The accepted location exactly matches the repeated acquisition candidate.
