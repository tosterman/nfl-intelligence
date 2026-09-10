# Fixed margin-scale diagnostic

Question: does a single calibration of forecast margin magnitude improve the model's later-season accuracy? Use the exact retained performance records in the current published artifact, not a refit of its base model. No market lines enter fitting or candidate predictions.

Fit one nonnegative coefficient on all 2024 records: minimize squared margin residuals with zero intercept, alpha = max(0, sum(predicted margin * actual margin) / sum(predicted margin squared)). No intercept preserves side-swap symmetry and keeps a zero projected margin at zero. Freeze alpha for every 2025 record, including postseason. Do not select cutoffs, priors or alternative coefficients after seeing results. Total forecasts remain unchanged; no probability or interval recalibration is claimed.

Primary diagnostic: 2025 candidate-minus-baseline margin MAE. Secondary: margin RMSE. Report uncertainty for paired absolute-error differences using the existing fixed 10,000 whole-week bootstrap, seed 20260910. Also report the unchanged closing-market benchmark on exactly matched 2025 games, separately from fitting. Check training/evaluation membership and outcome timing using the schedule; preserve artifact, schedule, protocol and code fingerprints.

The 2024–25 sample has already been used for development. This is a diagnostic experiment, not an untouched holdout or grounds for automatic production promotion. Improvement with an interval crossing zero is inconclusive. A worsened primary metric rejects this correction for now. Even a clear improvement requires independent future validation and reconciliation of score means, explanations, uncertainty and probabilities before release. Do not edit production site data or forecasts.
