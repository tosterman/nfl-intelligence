# Structural symmetry correction — 2026-09-10

The original EPA regression allowed a neutral-game margin intercept and symmetric sum features in its margin forecast, plus asymmetric differences in its total. Swapping team labels could therefore change the football prediction. This is a correctness defect irrespective of validation scores.

`fit_symmetric` now imposes separate designs: margin uses the home-venue indicator and signed difference features, with no intercept and no centering; total uses an intercept, venue and symmetric sum features. Margin scaling uses training-only root-mean-square feature scales, preserving zero. Total standardization is estimated on training-only rows and transformed back to raw coefficients. Forbidden coefficients remain exactly zero. Replay and inference call this one shared function.

The unchanged original grids were rerun. Selection still uses only 2021–2022 margin MAE (569 games); residual scales use only 2023. Previously inspected 2024–2025 remains development evaluation (570 games). Original experiment JSON and report were preserved. New detailed evidence is `reviews/symmetry-experiment-results.json`.

Selected parameters:

- Score half-life **180 days**, ridge **6**.
- EPA feature half-life **90 days**, ridge **10** (previous unconstrained selection was 100).
- Blend **75% score + 25% EPA**.
- 2023 blend residual RMSE: margin **13.537864904930167**, total **13.400742577616185**.

| Model | Validation margin MAE | Development margin MAE | Development total MAE | Development Brier | Development accuracy |
|---|---:|---:|---:|---:|---:|
| Original score 180/20 | 10.217 | 10.472 | 10.339 | 0.2301 | 61.69% |
| Selected score 180/6 | 10.081 | 10.253 | 10.310 | 0.2227 | 64.50% |
| Constrained EPA 90/10 | 10.121 | 10.066 | 10.305 | 0.2183 | 66.43% |
| Selected constrained blend | **10.043** | **10.159** | **10.251** | **0.2204** | **63.44%** |

Blend development margin MAE is 10.152 in 2024 and 10.165 in 2025. Nominal 80% margin coverage is 81.05%. The prior unconstrained blend's development margin MAE was slightly better (10.147); that does not justify retaining an invalid model structure. Historical market margin MAE remains better at 9.687. This correction is not a profitability claim or a new untouched holdout.

Five independent tests pass: prior future-feature and future-score perturbation checks, complete joins/finite features, end-to-end neutral team swaps, and symmetry under deliberately biased synthetic training. The neutral test also checks blended margin negation, total invariance, swapped expected scores and exact attribution. EPA decomposition multiplies raw features by raw coefficients; league and venue margin terms are exactly zero at neutral sites. Blend inference recomputes the scoring component in full precision before attribution, avoiding the previous tiny rounding remainder. Historical scoring replay retains its established three-decimal artifact values, so evaluated blend values can differ from full-precision inference by at most the scoring rounding contribution (0.000375 points at 75% weight).

Only `scripts/experiment_model.py`, `tests/test_experiment.py`, and the two new review artifacts were modified for this correction. Production refresh, site and ledger were not edited. The existing provenance, retrospective EPA vintage limitations, absent-personnel limitations and source licensing findings in `reviews/model-experiments.md` remain applicable.
