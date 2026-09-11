# Red-zone possession phases

`python scripts/audit_red_zone_phases.py` replays the retained 2025 source with a
possession-phase helper. It preserves source row order, stops at the first
touchdown by either team, and excludes conversion attempts. A source-classified
no-play can retain its pre-snap field position without inventing a scoring flag.

This resolves all ten discrepancies from the earlier exploratory audit and the
one apparent drive with two offenses: the extra rows were conversion penalties
after offensive or defensive touchdowns. Among 6,045 accepted fixed-drive groups,
1,823 have a pre-snap position strictly inside the 20 and 4,222 do not. All agree
with the provider's `drive_inside20` flag. Agreement is internal consistency with
the same source, not independent validation or official red-zone statistics.

One of 6,046 groups is still rejected: Cincinnati at Minnesota, 2025 Week 3,
fixed drive 20. Play 3284 is classified as a kickoff with an unset touchdown
flag; its description records offsetting penalties and no play. The helper does
not silently infer a zero scoring value. Resolve this with a documented,
source-pinned adjudication or a general source-supported rule before publication.

Play IDs are identifiers, not reliable sort keys. Arizona at New Orleans drive
16 lists timeout 3915 before field goal 3903. An initial monotonic-ID assumption
rejected 1,287 groups; preserving source order fixes that mistake. Duplicate and
invalid IDs remain rejected. Six regression tests cover touchdown/try boundaries,
defensive touchdowns, ordinary penalties, source order and unknown scoring state.

This helper is not integrated into the product. Completed-game cutoffs,
touchdown numerator reconciliation, coverage checks, the exact 20-yard boundary,
and presentation still require validation before any red-zone rate is published.
