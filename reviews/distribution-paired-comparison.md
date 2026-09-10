# Paired distribution sensitivity — 2026-09-10

Decision: retain research-only status. The mean-preserving correction repairs arithmetic, but this comparison does not establish predictive improvement or equivalence.

`python scripts/compare_distributions.py` compares the same selected empirical_bw2 candidate in saved v2 and v3 results. Input file SHA-256 hashes are retained in the result JSON. The routine requires matching source identities, candidates and complete game sets, rejects duplicates/nonfinite scores/season mismatches, and joins by game ID rather than row position.

For each metric and period, 10,000 paired weekly-cluster bootstrap resamples use seed 41023. Each season is resampled separately; each draw retains all games in a sampled season-week. The effect is the pooled sum of game differences divided by the sampled game count, not an unweighted mean of weekly averages. Differences are v3 minus v2, so negative favors v3. Intervals are 2.5th and 97.5th percentiles.

| Period | Games / weeks | Metric | Mean change | Bootstrap interval |
|---|---:|---|---:|---|
| 2021–22 | 569 / 44 | Negative log score | +0.000434 | [-0.000189, +0.001070] |
| 2021–22 | 569 / 44 | CRPS | +0.002648 | [-0.002002, +0.007512] |
| 2021–22 | 569 / 44 | Three-way Brier | +0.000096 | [-0.000265, +0.000466] |
| 2023 | 285 / 22 | Negative log score | +0.000301 | [-0.000437, +0.001030] |
| 2023 | 285 / 22 | CRPS | +0.001276 | [-0.004213, +0.006663] |
| 2023 | 285 / 22 | Three-way Brier | -0.000157 | [-0.000648, +0.000314] |

Every interval includes zero. This is a descriptive sensitivity check on reused development results, not prospective confirmation, equivalence testing, or evidence of betting profitability. It does not compare v3 against the normal reference because per-game reference records were not saved in the earlier artifacts. No new production predictions were generated.

## Limits and remaining work

Weekly clustering retains within-week pairing and shared exposure. It assumes weeks are exchangeable within each season and does not preserve cross-week dependence from repeated teams and overlapping training histories. It does not account for choosing bandwidth2, parameter estimation, revised historical inputs or multiple-comparison selection. Only 22 weekly clusters are available in the 2023 diagnostic. Wider contiguous-block sensitivity and prospective results are still needed.

The reason for avoiding independent-game resampling is dependence among observations. Contiguous-block resampling is a separate extension, not what this implementation claims to perform. See [Hyndman and Athanasopoulos, Forecasting: Principles and Practice](https://otexts.com/fpp3/bootstrap.html) for the time-series block-bootstrap rationale.

Three tests verify exact constant effects, row-order invariance, deterministic resampling, game-weighted estimates, nondegenerate intervals and failure on invalid/unmatched inputs. Existing v2/v3 evidence is preserved.
