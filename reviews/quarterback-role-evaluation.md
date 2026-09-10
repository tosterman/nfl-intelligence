# Historical quarterback-role agreement — September 10, 2026

The 2025 depth-chart archive is a feasible role signal, but its top-ranked player cannot safely stand in for a confirmed game quarterback. Evaluate this as source quality, not forecast accuracy or betting profitability.

## Measured result

Across 285 completed 2025-season games (570 team-games), using the newest team snapshot strictly before each cutoff and requiring age under thirty hours:

| Cutoff | Matching game QB ID | Different ID | Unavailable chart | Comparable coverage | Agreement among comparable |
|---|---:|---:|---:|---:|---:|
| 24 hours before kickoff | 495 | 47 | 28 | 95.09% | 91.33% |
| Immediately before kickoff | 517 | 49 | 4 | 99.30% | 91.34% |

All unavailable cases here were missing/stale prior charts. No game QB IDs were missing. The later cutoff improved coverage; conditional agreement was essentially unchanged. These overlapping samples do not prove a causal benefit or an optimal collection schedule. A matching ID alone does not establish announcement time, anticipated snaps, player health or in-game participation quality.

## Evidence and controls

`python scripts/evaluate_quarterback_roles.py` reads the verified file at `release-recovery/depth_charts_2025.csv` and current `data/games.csv`. The [depth-chart asset](https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2025.csv) is 52,917,870 bytes; hash `f5a4aa3fa70150e810b2255200c8735a6c1cc8ff77361308ce39149345b39b4a` matched GitHub release metadata. Exact observation rows and both source hashes are retained in `quarterback-role-evaluation.json`. This transformed analysis is attributed to nflverse under its repository's [CC BY 4.0 license](https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md).

Schedule kickoff times are interpreted in America/New_York, including daylight saving, following the [schedule dictionary](https://nflreadr.nflverse.com/articles/dictionary_schedules.html). Comparison uses the schedule's home/away QB ID fields as recorded game labels. It does not use those labels to choose the pregame chart. All-position team snapshots are indexed first, so a newer snapshot lacking QB rows cannot resurrect an older role. Exact-cutoff and future records are excluded. An independent output check verified all 1,140 observations are unique and every comparable chart is strictly prior and younger than thirty hours.

Historical depth timestamps describe provider loading; the files and schedule were acquired now and can contain retrospective corrections. This is not a verified historical vintage replay. The source comparison does not prove any improvement over the existing model. The two cutoffs were specified before this run; neither has been selected as a production setting based on these results.

## Consequence for the engine

Independent code review reproduced source hashes, both 570-team-game denominators, daylight-saving cutoff arithmetic, chart ages and ID comparisons. No material defect was found. The output field is named comparableCoverage to avoid conflating missing game labels with missing charts in future samples.

Use depth-chart leader identity as an uncertain feature with a fallback, not as ground-truth starting lineup. The next experiment must join strictly prior player performance, compare against team-only predictions, and retain explicit missing-data treatment. The roughly nine-percent mismatch rate motivates starter corroboration and scenario weighting; it does not itself supply calibrated probabilities for individual games. Production forecasts remain unchanged.
