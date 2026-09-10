# Discrete margin distribution experiment — 2026-09-10

**Recommendation: further validation; do not adopt this as a settlement-ready NFL distribution.** The symmetric empirical residual mixture modestly improves full-margin log score and CRPS, including on the separate 2023 check. However, every tested integer-bin distribution badly overpredicts ties. Simply integrating or rounding a smooth curve does not recover NFL scoring structure or validate key-number/push probabilities.

## Protocol

Hold the symmetric 75% score / 25% EPA mean forecast fixed. Reconstruct out-of-sample mean forecast residuals beginning in 2017. At each weekly cutoff, use only residuals from games dated before that cutoff. No target result or same-week future result enters the residual model. Candidate choice uses **mean discrete negative log score on 2021–2022 only** (569 games). Evaluate the selected candidate separately on 2023 (285 games). No 2024–2025 data are loaded.

Five declared candidates: normal with fixed sigma14, normal with chronological prior-residual RMSE, and symmetric empirical residual Gaussian mixtures with bandwidth1/2/4 points. Empirical residuals are rounded into an integer histogram and mirrored around zero, then Gaussian-smoothed; predictive mass is integrated over integer outcome bins. This symmetry is deliberate: swapping team labels negates mean and reverses the mass array. No fitted location shift is allowed.

All distributions use the same integer bins from -100 through100; endpoint bins contain tail overflow. Negative log score evaluates probability of the actual integer margin. CRPS is computed as the sum of squared cumulative-distribution discrepancies over integer intervals, in points. A three-outcome Brier score uses away win/tie/home win and is not directly comparable to the site's decisive-game binary Brier. Proper scoring rules assess the whole probability forecast rather than only the most likely outcome. [Gneiting and Raftery, primary paper](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf).

The fixed14 reference represents the existing normal-family assumption integrated into integer bins for comparable mass scoring. It is not a claim that the site's continuous normal model already contains a calibrated tie probability. Using the 2023-fitted production residual scale to choose on 2021–2022 would introduce chronology leakage, so this experiment does not do that.

## Selection results

| Candidate | 2021–2022 log score ↓ | CRPS ↓ | 80% coverage | Mean interval width |
|---|---:|---:|---:|---:|
| Normal sigma14 | 3.98451 | 7.25703 | 83.48% | 35.87 |
| Normal fitted scale | 3.97948 | 7.24146 | 81.72% | 34.17 |
| Empirical bandwidth1 | 3.97458 | 7.23166 | 81.55% | 33.85 |
| **Empirical bandwidth2** | **3.97394** | **7.23249** | **81.55%** | **33.97** |
| Empirical bandwidth4 | 3.97829 | 7.23954 | 82.78% | 35.09 |

Selection uses log score, so bandwidth2 wins even though bandwidth1 has slightly better CRPS. The underlying point model itself was previously selected on these validation years; these results do not represent an untouched model-selection sample or establish statistical significance.

## Separate 2023 check

| Candidate | Log score ↓ | CRPS ↓ | 80% coverage | Mean width | Three-outcome Brier ↓ |
|---|---:|---:|---:|---:|---:|
| Normal sigma14 | 4.02554 | 7.57242 | 80.70% | 35.90 | 0.46011 |
| Selected empirical bandwidth2 | 4.01801 | 7.55727 | 78.60% | 33.78 | 0.46062 |

The selected mixture improves log score by0.00754 and CRPS by0.01515 points, but has slightly worse three-outcome Brier and lower interval coverage. These are modest changes, not a simulation breakthrough.

## Why adoption is withheld

Tie calibration is plainly poor. In 2021–2022 the selected model predicts **17.34 ties versus3 observed**; the normal reference predicts15.31. In 2023 the selected model predicts **8.68 ties versus0 observed**; the normal reference predicts7.62. The pooled model also assigns nonzero tie mass to postseason games. NFL postseason games cannot end tied, so this is not a valid postseason settlement model. [NFL overtime rules](https://nfl-ops-prod-umbraco-author.azurewebsites.net/rules-officiating/featured-rules/overtime-rules/).

Do not publish these tie masses, cover/push probabilities, or “10,000 simulated games” as verified football probabilities. There is no evidence here that the mass at3,7,10 or other scoring margins is calibrated. A symmetric residual histogram centered on a continuously varying mean does not preserve football's unconditional scoring atoms. The pooled residual approach also ignores differences in overtime rules, season type and conditional uncertainty.

A defensible next design would explicitly separate regulation/overtime or fit a final-margin discrete model with historical season-specific support, zero postseason tie probability, and calibrated regular-season tie behavior. Freeze that design and evaluate on a new forward period. Do not fix tie probability after seeing2023 and then call the same period an untouched validation set.

## Files and verification

`scripts/experiment_distribution.py`, `tests/test_distribution_experiment.py`, and `reviews/distribution-experiment-results.json` contain the independent implementation and full evidence. Four tests passed: normalization/nonnegative mass with team-swap symmetry, zero-mean three-outcome consistency, proper-score sanity checks, and future-residual perturbation. Existing model scripts and production artifacts were not edited. The computation uses SciPy's normal CDF in this research module; any integration must explicitly declare that dependency.

The existing retrospective input-vintage limitations remain: modern revised EPA is not an archived contemporary dataset. Completed-game availability is approximated using prior dates and a weekly freeze, not proven source publication times. This experiment improves the distribution research harness; it does not close the founding document's football simulation requirement.
