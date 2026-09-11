# Historical inside-20 publication artifact

`python scripts/build_red_zone_evidence.py` creates `data/red-zone.json` from
the exact retained play-by-play and schedule archives plus the source-pinned
kickoff adjudication. It includes 5,998 possessions in 285 games, all 32 teams,
per-possession entry IDs and outcomes, and offense/defense aggregate counts.

Both sides reconcile to 1,824 inside-20 possessions and 1,046 offensive
touchdowns. The artifact describes a pre-snap position strictly inside the 20,
including regular season and playoffs, with one count per possession. It does
not claim official league statistics or adjust for opponents, personnel or age.

The builder requires completed scores and dates strictly before the cutoff,
matches every retained play to a schedule game, verifies dates and participants,
rejects duplicate plays/missing drive IDs, and requires both offenses for every
eligible game. Empty evidence cannot produce a publication artifact. Exact
compressed source digests and the adjudication hash are retained. Hash checks
protect reproducibility; coverage checks do not prove the provider omitted no
individual plays inside a represented game.

Fourteen red-zone tests pass, including full artifact replay, all-team coverage,
offense/defense conservation, an official-gamebook sample, strict cutoffs,
unfinished games, missing offense coverage, mismatched context and duplicate
plays. This artifact is not yet imported by the application. UI integration and
review remain before showing these rates to readers.
