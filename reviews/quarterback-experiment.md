# Quarterback residual experiment

Decision: retain the production model. The candidate has a small descriptive improvement, but this experiment does not establish a reliable improvement or profitable betting edge.

The fixed specification fits two passing-form differences to baseline margin residuals: net passing yards per dropback and ten times the opposite sack-rate difference. Ridge is 10, with no intercept. Swapping teams negates the adjustment. Missing either quarterback feature leaves the baseline unchanged. Totals and probabilities are not changed.

Fit: 118 games with both features in 2025 weeks 1–8. Evaluation: all 164 games from week 9 through the postseason, including 15 fallback games. The latest training outcome's 24-hour embargo ends October 29 at 00:15 UTC; the first evaluation feature cutoff is October 30 at 00:15 UTC. This uses a publication-time proxy, not verified historical receipt timestamps.

| Evaluation measure | Baseline | Candidate |
| --- | ---: | ---: |
| Margin MAE, all 164 games | 10.0416 | 9.9828 |
| Margin RMSE, all 164 games | 12.6036 | 12.5248 |
| Margin MAE, 149 comparable games | 10.0802 | 10.0155 |

Candidate-minus-baseline MAE is −0.0588 points. A paired bootstrap resampling 14 entire weeks, with 10,000 draws and seed 31025, gives a descriptive 95% percentile interval of **−0.3139 to +0.1979** points. It crosses zero. Week clusters preserve within-week game dependence but do not account for all cross-week dependence or uncertainty from fitting the coefficients.

2025 has already been used for development elsewhere in this project. This is a chronological development split, **not an untouched holdout**. Depth-chart roles are not confirmed starters; corrected historical player files are not vintage snapshots. Passing form excludes rushing, opponent adjustment, and causal isolation from line, scheme, and receiver effects. None of these results justify probability, wagering, or revenue claims.

The experiment initially rejected a schedule hash mismatch between deployed site data and local feature inputs. It now reconstructs the baseline from the exact schedule snapshot used for features, with cached team statistics. The result JSON records input and code hashes, coefficients, all game records, fallback coverage, timing checks, and weekly deltas. Production files are not modified.

Reproduce with `python scripts/experiment_quarterback.py` after acquiring the hash-verified feature inputs and cached 2010–2025 team statistics. Tests cover swap symmetry, missing-data fallback, ridge arithmetic, paired differences, and week grouping. Further work should use a separately declared evaluation protocol and broader chronological seasons or prospective observations; tuning this split until it wins would weaken the evidence.

Independent code review reproduced the coefficients, checked the feature hash and 285 unique game records, verified fallback and the timing guard, and found no material defect. All three targeted tests passed. This is an automated adversarial review, not independent expert endorsement.
