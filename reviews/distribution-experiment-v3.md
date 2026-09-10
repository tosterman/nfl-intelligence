# Mean-preserving discrete margin research — 2026-09-10

Decision: mathematical reconciliation passes; do not promote this candidate to production.

The v2 tie adjustment proportionally redistributed zero-margin mass and could change the expected margin. V3 fixes tie probability, then exponentially tilts the positive nonzero-margin probabilities until their conditional expectation equals model margin divided by one minus tie probability. Log-space normalization avoids overflow. The solver preserves support and fails explicitly for nonfinite/negative mass, invalid constraints, degenerate support, or targets outside or on its attainable boundaries. Boundary distributions require a separate degenerate-limit implementation and are deliberately rejected.

## Protocol and evidence

Command: `python scripts/experiment_distribution.py --mean-preserving`.
All five declared candidates rerun on the chronological 2017–2023 baseline replay. Prior residuals and regular-season tie fitting use dates strictly before the current weekly cutoff. The tie prior is unchanged: Beta(1,99), with postseason tie probability zero. Candidate selection uses 569 games in 2021–2022; the 285 games in 2023 are reused development diagnostics, not an untouched holdout. No 2024–2025 outcomes enter this experiment. Previous v1/v2 result files are retained.

| Metric | V3 normal14, 2021–22 | V3 empirical bw2, 2021–22 | V3 normal14, 2023 | V3 empirical bw2, 2023 |
|---|---:|---:|---:|---:|
| Negative log score, lower better | 3.971698 | 3.957935 | 4.002956 | 3.991653 |
| CRPS, lower better | 7.268429 | 7.238267 | 7.582870 | 7.561877 |
| Central 80% coverage | 84.01% | 82.07% | 81.05% | 78.95% |
| Three-outcome Brier, lower better | 0.458541 | 0.456966 | 0.459055 | 0.459266 |

Maximum absolute mean discrepancy was at most 7.11e-15 points in every reported candidate/period. Expected ties remain 2.466 versus three observed in 2021–22, and 1.214 versus zero in 2023. The bw2 candidate is still selected by the declared development log-score criterion. Its small full-margin score improvement does not demonstrate profitability or prospective superiority; its 2023 three-outcome Brier is slightly worse than the normal reference.

The saved v2 and v3 source identities match. Paired bw2 comparisons on identical game IDs show v3 negative log score worsening by 0.000434 on 2021–22 and 0.000301 on 2023 relative to v2. This correction is justified by coherent moments, not by an improvement over v2. These tiny observed differences have no uncertainty estimate and should not be treated as statistically established performance changes.

## Verification and independent review

Ten distribution tests pass, including mean recovery, fixed tie mass, normalization, nonnegative finite probabilities, input immutability, reflected team-swap symmetry, preserved zero support, infeasible/invalid input rejection, identity when constraints already hold, near-boundary numerical stability, and future-record perturbation with the new correction enabled.

An independent code/math reviewer confirmed the conditional-mean derivation and identified remaining acceptance work: endpoint overflow sensitivity, wider numerical support, separate zero-probability outcome counts (the current scoring floor can mask these), paired uncertainty estimates, and prospective evaluation. The current ±100 endpoint bins aggregate overflow but their moments treat that overflow as exactly ±100. No arbitrary epsilon is added to restore numerically lost support. Exponential tilting can change variance, skewness, intervals, win chances and push probabilities. It does not create a joint integer-score model or validate football key numbers.

Full records and source identities: `reviews/distribution-experiment-v3-results.json`. Production engine, forecast ledger, publication receipts and public predictions are unchanged.

## Follow-up uncertainty check

The paired weekly-cluster analysis in `reviews/distribution-paired-comparison.md` now provides descriptive uncertainty intervals for the v3 versus v2 changes. All six intervals include zero. Its limitations include reused development data, candidate selection and unmodeled cross-week dependence; it does not establish equivalence or justify promotion.
