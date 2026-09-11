# Retained weather revisions

Founding section 21 calls for understandable changes between visits, including
weather. Game pages now compare the latest two retained forecast issues for the
same game, kickoff, venue and exact location-evidence identity. An opening-brief
link appears when their conditions differ. Expandable history retains issue and
capture times, raw wind text and source fingerprints. It remains explicitly
historical when the current forecast is stale; no weather model effect is claimed.

`scripts/weather_history.py` reproduced all 123 retained observations from their
compressed NWS responses. It verifies observation and source hashes, recorded
venue evidence, the point-to-forecast URL mapping, pregame acquisition, and every
kickoff-period value. This produced 29 distinct issues across the recorded
game/location contexts. Duplicate acquisitions collapse in the UI; contradictory
values for one issue fail closed. Location-method changes are not merged.

The compact artifact is rebuilt after weather acquisition, included in native
Git and direct release files and recovery uploads, and checked before publication.
An independent review caught the missing native staging entry; it was added.
Three Python provenance/replay tests, four TypeScript comparison tests, fourteen
publication tests, TypeScript checking and the production build passed.

The browser check covers unchanged Atlanta–Pittsburgh and changed Dallas–New York
in Chromium/WebKit at 320, 390 and 1280px, including keyboard disclosure, opening
link focus, source fingerprints, overflow and bounded automated accessibility.
The first script version had an ambiguous multi-element assertion; the expanded
test also initially expected an incorrect wind direction. Both test expectations
were corrected against the retained evidence. Neither was a product defect.

The 390px expanded Dallas–New York history was visually inspected. This is
bounded local evidence, not a human comprehension study or a public deployment.
The engine, forecast snapshots and numerical predictions were not modified.
Repository JSON fingerprints normalize CRLF to Git's LF line endings for
Windows/Linux portability; raw upstream response fingerprints remain exact.
A fourth Python test checks this normalization and rejects content changes.
