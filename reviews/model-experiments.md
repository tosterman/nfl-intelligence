# Model experiments — 2026-09-10

## Decision

A measured, modest improvement is feasible. Validation selects a **75% scoring model / 25% EPA regression blend**. The scoring component uses a 180-day half-life and ridge 6, versus the original ridge 20. The EPA component uses a 90-day feature half-life and ridge 100. Do not promote standalone EPA because it happens to beat the blend on development data; that would change the selection procedure after inspecting the evaluation.

This is not demonstrated market outperformance. Historical market margin MAE is **9.687** on the same 570 development games, better than every tested candidate. Historical market total MAE is **10.096**, also better than the selected blend. These are retrospective price benchmarks with unverified vintage quote availability.

## Measured results

All candidates selected on 2021–2022 only (569 games). Probability residual scales estimated on 2023 only. The previously inspected 2024–2025 period is explicitly **development evaluation**, not an untouched holdout. The run was repeated to correct the original-model comparison from 365/20 to the actual production baseline 180/20; the selection rules and grids did not change. Validation Brier uses the declared fixed 14-point residual scale, while development uses 2023 residual scales.

| Model | Validation margin MAE | Development margin MAE | Development total MAE | Development Brier | Development accuracy |
|---|---:|---:|---:|---:|---:|
| Original score 180/20 | 10.217 | 10.472 | 10.339 | 0.2301 | 61.69% |
| Selected score 180/6 | 10.081 | 10.253 | 10.310 | 0.2227 | 64.50% |
| Selected EPA 90/100 | 10.178 | 10.051 | 10.359 | 0.2177 | 66.43% |
| Selected 25% EPA blend | **10.057** | **10.147** | **10.259** | **0.2201** | **63.80%** |

Blend margin MAE: 2024 **10.137**, 2025 **10.157**. Blend straight-up accuracy fell from 66.67% in 2024 to 60.92% in 2025; a stronger MAE does not imply every headline metric improves. Blend 80% margin interval coverage is 80.70%, using a 2023 margin residual RMSE of 13.5323 and total RMSE 13.4126. Ties are excluded from probability/accuracy scoring. No claim of statistical significance is made; validation improvement of the blend over the retuned score model is only 0.024 points.

## Exact approach

`scripts/experiment_model.py` is isolated from production exports. It records the full 30-member score grid, 9-member EPA grid and 5 blend weights in `reviews/model-experiment-results.json`. Score grid: half-life 90/180/270/365/540 days × ridge 1/3/6/12/20/60. EPA grid: half-life 90/180/365 × ridge 10/100/1000. Blend EPA weights: 0/.25/.5/.75/1. Selection minimizes validation margin MAE, including for the blend; totals were not optimized separately.

EPA features use game-level passing EPA per dropback, rushing EPA per carry, passing CPOE, sacks suffered/dropback, interceptions/dropback, lost fumbles/play, and pass share. Dropbacks are attempts + sacks suffered. Carries include the source's scramble/kneel conventions. The defensive side is derived from the opposing offense's recorded statistics in the same historical game, not inferred from defensive tackle counts.

For each team, use a time-weighted average of prior games with two pseudo-games of zero shrinkage. This simple shrinkage is an experimental modeling choice, not missing-data imputation. Features are the home versus away offense/opponent-allowed differences and sums; a ridge model maps them to margin and total. Standardization, intercept and coefficients are fit on earlier completed game rows only, beginning in 2014. Feature histories begin in 2010. Weekly feature state freezes before the week's earliest game. These are additive profile matchups, not validated nonlinear scheme interactions or player effects.

## Reusable inference and verification

`infer_epa(history, statmap, targets)` produces expected score, margin, total, feature values, training bounds and exact additive margin contributions. `infer_blend(...)` combines it with the validation-selected scoring baseline. The caller must filter history to genuinely available completed games before its real forecast cutoff. The experiment does not establish historical availability timestamps.

Contribution names retain offense versus opponent-allowed meaning. Every EPA margin coefficient contribution sums exactly to EPA predicted margin. The score model rounds its values, so production should preserve full precision or explicitly reconcile its tiny rounding remainder before combining attribution. Do not convert CPOE or passing EPA contributions into statements about today's QB or missing defenders. These modules have no verified personnel input.

`tests/test_experiment.py`: **3 tests passed**. They perturb all target/future EPA statistics without changing target features; perturb future/target final scores without changing current inference; verify complete source joins and finite features. All 8,726 team-game records from 2010–2025 join successfully, and passing EPA, rushing EPA, CPOE and lost-fumble fields have no blank values. Tests do not prove upstream expected-points models were trained only on historical information. Revised EPA and CPOE can inherit their own upstream vintage/model leakage, so describe this as retrospective research.

## Source and current-season feasibility

Exact source pattern, verified from official loader source: `https://github.com/nflverse/nflverse-data/releases/download/stats_team/stats_team_week_{season}.csv`. Downloads 2010–2026 are in `data/raw/`; the 2026 artifact currently contains two team rows for `2026_01_NE_SEA`. Presence of a file does not imply complete current-week coverage. Download metadata includes local acquisition time, SHA-256, row count, season, latest week, license link and timestamp meaning. Local acquisition is not upstream publication time. The current-season download was added after the evaluation and does not participate in its fitting or selection.

The official repository declares CC BY 4.0. Preserve attribution to nflverse and link the source license; distinguish this from software MIT licensing. The official data dictionary describes passing EPA as EPA on attempts and sacks; the loader explicitly supplies weekly team statistics. [Repository and license](https://github.com/nflverse/nflverse-data), [official loader](https://github.com/nflverse/nflreadr/blob/main/R/load_stats.R), [team stats documentation](https://nflreadr.nflverse.com/reference/load_team_stats.html), [dictionary](https://nflreadr.nflverse.com/articles/dictionary_team_stats.html).

The official update schedule says team statistics follow play-by-play updates, generally nightly after game days with corrections later in the week. It also says the injury source ended after 2024 and has no ETA for restoration; that is another reason not to infer current injury knowledge from nflverse availability. Treat this documentation as source-reported operational status and verify fresh source coverage each run. [Official availability schedule](https://nflreadr.nflverse.com/articles/nflverse_data_schedule.html).

If 2026 team stats are unavailable or missing a required completed game, either keep a clearly timestamped prior snapshot or publish an explicitly labeled score-only fallback with its own version and calibration. Never silently substitute zero EPA or claim full freshness. Current-week game fact cards can show historically weighted passing/rushing profiles and opponent-allowed profiles even before a richer personnel model exists, with cutoff and sample information attached.

## Recommended next step

Integrate the selected blend under a new version while preserving all existing snapshots. Keep the pure EPA challenger in the research report. Freeze this model before observing 2026 outcomes, retain publication receipts, and evaluate forward. Substantial additional progress should test opponent-adjusted efficiency and separately validated pace/total modeling with a new forward evaluation period, rather than keep mining 2024–2025.
