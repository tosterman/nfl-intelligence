# Weekly matchup panels

Both big-play and inside-20 panels now separate the current-season sample from
the retained prior-season history. Exact season, phase and week matching is
required; source freshness expires at the older provider asset update plus 30
hours. An open tab replaces expired current content without hiding historical
evidence. The selector relies on builder-validated count integrity.

Current Week 1 evidence correctly has no eligible earlier games. The UI explains
that state without showing zero rates. Future available samples show pooled
numerators/denominators, offensive and defensive game counts, weekly cutoff and
collection time. A zero inside-20 denominator is unavailable, not zero percent.
These descriptive rates do not change forecasts.

Validation: 164 application tests and TypeScript passed; all four acquisition
tests reproduce the refreshed artifact. Twelve browser cases cover Chromium and
WebKit at 320/390/1280px on a forecast and a no-forecast game. Both panels displayed
the empty sample, expired correctly under a controlled clock and preserved the
prior-season section with no document overflow or page errors. Final 390px visual
inspection and a Chromium axe scan found no tested WCAG violations. Small label
and selector refinements were followed by targeted tests. Independent code review
found no material defect.

Available-sample rates and zero denominators now also have six static browser
fixture checks: Chromium/WebKit at 320/390/1280px, with actual app CSS explicitly
verified as applied. Fixtures are visibly labeled synthetic and never published
as NFL results. The check verifies four tables, opposing-column counts, no
overflow and no tested WCAG violations. Visual inspection caught an awkwardly
wrapped unavailable label; zero-denominator cells now use a dash with accessible
Unavailable text and retain their sample counts. All 165 application tests pass.

Initial fixture attempts exposed harness issues: live development scripts could
replace the fixture DOM, and an isolated document initially missed its stylesheet.
Those runs are not counted as final verification. The fixture now uses a fresh
document with copied CSS and a computed-style assertion. Final results are in
`weekly-populated-browser.json` and `weekly-populated-fixture.png`.

Missing prior-season evidence no longer suppresses the independent current-season
panel. A regression covers that branch, and the empty-state copy does not promise
historical data that might be unavailable. Actual prior-season data rotation,
real eligible current-season samples, hosted refresh and public publication
verification remain outstanding.
