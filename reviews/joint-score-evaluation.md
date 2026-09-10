# Joint-score evaluation: promising, inconclusive

The protocol was committed as `f13a695` before execution. Both priors use 3,793 completed games from 2010–2023; no 2024–2025 outcomes enter distribution fitting. The empirical candidate combines mirrored score-pair counts with 100 independent-marginal pseudogames. The reference uses a discrete Gaussian grid with the historical score covariance, approximately 102.13 points squared per team and -4.84 cross-team covariance. It is deliberately overdispersed relative to a Poisson count model.

Both distributions are reconciled to the same retained expected home/away scores and the same tie constraint. The 285 evaluation games are the published model's 2025 historical development records, including postseason. No games were omitted, no zero probabilities were clipped and no point forecasts were refitted.

| Measure, lower is better | Empirical joint candidate | Gaussian grid reference |
|---|---:|---:|
| Joint final-score negative log score | 7.15993 | 7.26441 |
| Margin negative log score | 3.83440 | 3.96913 |
| Total negative log score | 4.00588 | 4.00146 |
| Margin CRPS | 7.28699 | 7.30589 |
| Total CRPS | 7.53259 | 7.52696 |
| Win/tie/loss Brier | 0.45137 | 0.45017 |

The primary paired joint-log-score difference is **-0.10448**, with a whole-week resampled 95% interval of **-0.32836 to +0.12212**. Negative favors the candidate. The interval spans zero, and total-score and three-outcome metrics slightly favor the reference. These results do not justify production promotion or establish equivalence.

Expected ties were 0.948 versus one observed. That aggregate agreement is not tie calibration: only one event occurred, historical overtime eras are pooled, and postseason zero ties are imposed by construction. Maximum expected-team-score reconciliation error was below 9.90e-10 points across the complete evaluation.

Three evaluation tests verify exact point-mass scores, known two-outcome log/CRPS/Brier arithmetic and exclusion of future outcomes from frozen priors. Six solver tests separately cover moments, settlement constraints and numerical behavior. Artifact, schedule, protocol, prior-fit information and code fingerprints are preserved with every game's scores in the JSON report.

Independent review reproduced all 570 candidate/reference distributions, fitted priors, per-game scores and paired bootstrap. It verified the scoring formulas and passed all three evaluation tests without finding a material defect.

This is a comparison of two bounded research distributions, not the site's continuous normal approximation. Reused development outcomes, current revised inputs, the 0–100 grid, fixed shape and incomplete dependence-aware uncertainty limit interpretation. Key-number probabilities, extreme tails, current-rule overtime behavior, closing-line settlement performance and prospective validation remain unverified. Keep production unchanged and retain this candidate for a separately declared future evaluation; do not tune its smoothing on these same results.
