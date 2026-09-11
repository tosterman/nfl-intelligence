# Explosive-play matchup evidence

Build descriptive offense and defense evidence from retained nflverse play-by-play.
Use completed games strictly before the supplied weekly date cutoff, matched by
game ID, date and home/away teams to the schedule. Initially use the 2025 season;
label it as historical evidence with equally weighted eligible plays. Pool the
numerators and denominators; do not average game-level rates. Do not change frozen forecasts.

Define an explosive passing play as a source `pass` play with at least 20 yards
gained, and an explosive run as a source `run` play with at least 10 yards gained.
These are this publication's chosen thresholds. Passing plays include sacks;
runs include scrambles. Exclude two-point attempts, no-play records, kneels, spikes and special teams.
Keep valid pass/run plays with penalties using the source's credited yards.
Do not reinterpret descriptions to override source scoring.

Retain exact compressed source bytes and their SHA-256. Reject duplicate play
identities, missing/nonfinite yards, inconsistent participants and inconsistent
dates. Store per-game numerators and denominators, with offense and defense
counts derived from the same eligible plays. Zero eligible plays means no rate.

Acceptance: hand-counted boundary and cutoff tests; reproduce all season counts
from retained bytes; reconcile offense and defense totals; independently review
definitions before connecting the artifact to matchup pages. Red-zone drive
conversion requires a separate possession/outcome definition and is not inferred
from touchdown plays. UI must expose sample sizes, season, cutoff and attribution.
