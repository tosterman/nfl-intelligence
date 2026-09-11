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

Available-sample rates and zero denominators are covered by rendered fixture
tests, not by current-season live browser data. Real eligible games, positive
sample browser inspection, prior-season rollover, hosted refresh and public
publication verification remain outstanding.
