# Rest differential experiment — 2026-09-10

**Decision: reject a predictive rest adjustment for now.** The no-rest baseline wins the declared 2021–2022 selection against every tested rest configuration. These results do not show that rest never matters; they show insufficient incremental value for this bounded feature on top of the existing scoring/efficiency blend. Descriptive rest-day context is feasible, but should not be assigned a model point value without evidence.

## Method

The fixed foundation is the symmetric 75% score / 25% EPA blend: score half-life180/ridge6, EPA half-life90/ridge10. Generate chronological out-of-sample baseline residuals for 2017–2020, then update the residual regression using only games before each target's weekly cutoff. The rest correction has one coefficient, no intercept: points adjustment = coefficient × rest-day difference. Total remains unchanged. This structure preserves team-swap margin symmetry and leaves zero rest difference at zero adjustment.

Derive rest from the most recent **same-season completed game date strictly before the week's first game**. Never read the source's stored home_rest/away_rest fields. Unknown previous-game dates, including opening week, produce explicit unavailable evidence and an abstaining zero correction. The experiment does not confuse a six-month offseason with recovery advantage. Derive each team's day gap from its prior game to the target scheduled date, cap each gap, then subtract away from home.

Declared alternatives: no rest, plus cap14/cap21 days × ridge0/100/1000. Select only by 2021–2022 margin MAE on 569 games. The foundation was already selected using these years, so this is reused development selection and carries multiple-comparison risk. A separate 2023 check uses 285 games and fixed 14-point probability scale. **No 2024–2025 data were used for fitting, selection or evaluation.**

## Selection results

| Configuration | 2021–2022 margin MAE |
|---|---:|
| No rest | **10.042961536** |
| Cap14, ridge0 | 10.044272622 |
| Cap14, ridge100 | 10.044240213 |
| Cap14, ridge1000 | 10.043983394 |
| Cap21, ridge0 | 10.043427491 |
| Cap21, ridge100 | 10.043415900 |
| Cap21, ridge1000 | 10.043325919 |

The best rest challenger loses by 0.000364 points per game. This is negligible, but there is no justification to add a numerical module when it fails even its own selection objective. Validation Brier likewise favors the baseline: 0.2264067 versus 0.2264536 for the best rest challenger. Straight-up accuracy is identical across these configurations at 63.07%.

The selected no-rest model's separate 2023 margin MAE is **10.452249132**, total MAE **10.558208701**, and Brier **0.229512933**. The validation-ranked rest challenger has 2023 margin MAE **10.450980948** and Brier **0.228955500**, a tiny 0.001268-point MAE improvement. This diagnostic check cannot replace the 2021–2022 selection and is insufficient evidence to reverse the rejection.

## Evidence and limits

`scripts/experiment_rest.py` is an independent experiment and writes only `reviews/rest-experiment-results.json`. It includes full selection metrics, separate 2023 metrics, and game-level prediction evidence. Source weekly efficiency artifacts retain the existing URLs, hashes and license metadata; schedules come from the checked-in `data/games.csv`. Original scores, model files, site, and ledger are untouched.

Five tests passed in `tests/test_rest_experiment.py`: strict date-cutoff exclusion, future residual perturbation, team-swap sign symmetry, offseason/unavailable-history handling, and ignoring both uncompleted rows and source-provided rest fields. Historical completion availability is approximated by previous calendar dates; the file is not a vintage schedule archive. A later rescheduling correction could differ from what was known before a real forecast, and the existing EPA vintage limitations remain. Rest-day differences are associations, not demonstrated causal effects. This experiment does not test travel, altitude, circadian effects, preparation quality, or personnel recovery.

Preserve the rejection as a research result. A future investigation could use genuinely timestamped schedule and availability records or a predefined short-rest interaction with travel, evaluated prospectively. Do not keep changing rest cutoffs until a reused season improves.
