# Historical explosive-play evidence

The first retained artifact covers all 285 completed 2025 games (regular season
and postseason), 570 offense-game samples and 32 teams, using the current site's
weekly cutoff of 2026-09-09. It is descriptive and unweighted. It is not connected
to the forecast model or public matchup pages yet.

| Source classification | Eligible plays | Explosive plays | Definition |
| --- | ---: | ---: | --- |
| Passing, including sacks | 19,737 | 1,639 | At least 20 credited yards |
| Rushing, including scrambles | 14,895 | 1,661 | At least 10 credited yards |

The source contains 48,771 total rows. No-play records, special teams, kneels,
spikes and non-play rows do not enter these denominators. A penalty flag alone
does not remove a valid credited play. These definitions follow the source's
play classification, rather than treating its pass count as official attempts.

Exact original compressed play-by-play bytes (19,105,296 bytes) are retained at
`data/pbp-sources/2f135887790a013fd004e609e37096bb4816d5cc80b9f19122e1bad478961978.csv.gz`.
The manifest also pins the schedule, source attribution and retention timestamp.
Retention time is not a claim that these historical data vintages existed before
the games. This evidence must not be used to assert prospective betting results.

Rebuild offline with `python scripts/build_explosive_evidence.py`. Eight targeted
tests verify threshold boundaries, denominator exclusions, strict cutoff,
unfinished games, duplicate records, corrupt fields, digest rejection, missing
game coverage, full retained reproduction and offense/defense reconciliation.
Run `python -m unittest discover -s tests -p test_explosive*.py`.

A separate CSV extraction reconciles Arizona at New Orleans, 2025 Week 1:
Arizona 2/34 passing and 4/27 rushing; New Orleans 1/45 passing and 3/22 rushing.
`explosive-play-sample.json` lists the contributing play IDs and descriptions,
including a credited scramble with an additional defensive penalty.

Limitations: the coverage guard detects missing offense-game groups, not every
possible omitted play inside an otherwise present game. The retained source hash
prevents subsequent alteration; it cannot prove the provider's original file is
error-free. No independent reviewer sign-off is recorded: the requested reviewer
could not run because its usage allowance was exhausted. Red-zone possession
definitions, UI integration and independent football review remain open.

Definitions: [nflreadr play-by-play documentation](https://nflreadr.nflverse.com/reference/load_pbp.html)
and the retained [source dictionary](https://raw.githubusercontent.com/nflverse/nflreadr/main/data-raw/dictionary_pbp.csv).
