# Conversion-attempt correction

Red-zone definition research exposed a flaw in the initial explosive-play
denominators: nflverse classifies two-point attempts as pass/run records.
The original filter therefore counted 98 passing tries and 32 rushing tries.
These are now excluded using `two_point_attempt`, and missing classification
fails rather than silently treating an unknown record as an ordinary play.

The regression test first reproduced the extra passing/rushing denominator;
it passes with the filter. The same retained source bytes now reproduce 19,639
passing plays and 14,863 rushing plays. Explosive numerators remain 1,639 and
1,661. All 285 games and 570 offense-game groups remain represented. No frozen
forecast code, forecasts or source bytes were changed.

The fixed SF/LA component sample was updated using the rebuilt counts. For
example, SF passing is 55/664 (8.3%), rather than 55/669 (8.2%). The artifact
explicitly records `excludesTwoPointAttempts: true`, and UI definitions disclose
the exclusion. Earlier browser screenshots describe the earlier revision and
must not be used as evidence for these corrected values.

Red-zone work remains exploratory. Grouping the 48,771 source rows into 6,046
fixed-drive groups and checking pre-snap field position strictly inside the 20
agrees with the provider's inside-20 flag for 6,036 groups; ten disagree.
The disagreements include post-touchdown conversion penalties where the
conversion flag itself is zero. One filtered drive still contains two offense
identities. `red-zone-definition-audit.json` retains the exact examples. A
simple yard-line filter is insufficient: next work must identify touchdown/try
boundaries and reconcile drive ownership before publishing possession rates.
