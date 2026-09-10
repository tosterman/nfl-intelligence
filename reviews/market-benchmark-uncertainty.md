# Matched closing-market benchmark uncertainty

This audit uses the exact 570 historical records in the published `score-efficiency-v1.2.0` artifact generated September 10, 2026 at 18:57:30 UTC. It does not refit the model or substitute a newer schedule. The full artifact hash is recorded with calculation-code hashes and every paired error in the JSON result.

| Outcome | Matched games | Model MAE | Closing-market MAE | Model minus market | Resampled 95% interval |
|---|---:|---:|---:|---:|---:|
| Home margin | 570 | 10.1589 | 9.6868 | +0.4721 | +0.2618 to +0.6963 |
| Total points | 570 | 10.2510 | 10.0956 | +0.1553 | -0.0230 to +0.3332 |

Positive differences favor the closing market. The margin comparison consistently favors the market under this resampling method. The total interval includes zero; that does not prove equivalence. Neither comparison establishes executable betting returns. Closing prices contain information that may not have been available when an earlier model forecast was generated, so this is a demanding outcome benchmark, not a matched-information timing experiment.

## Method and limitations

For each outcome separately, include only games with a market line and finite model/outcome values. Compute both absolute errors on that exact pair, then their difference. Within each of the two seasons, sample its 22 whole week clusters with replacement, preserving all games within each selected cluster. Pool summed differences divided by sampled game counts; this weights games rather than giving a sparse postseason week equal influence to a full regular-season week. Repeat 10,000 times with seed 20260910 and take percentile endpoints. No multiple alternatives or favorable seeds were selected.

The historical 2024–25 sample is reused development data. Current revised source records are not historical vintages. Treating weeks as independent does not capture team dependence across weeks, model-selection uncertainty or all sources of sampling error. These are descriptive intervals under stated assumptions, not prospective validation or causal claims.

Three focused tests verify a known constant paired difference, unequal-size whole-week weighting with analytically bounded resamples, matched exclusions, empty/sparse results, invalid values, duplicate game rejection and deterministic ordering. The initially failing ordering test exposed input-order differences in retained records; sorting by season/week/game now makes the complete result deterministic.

Independent review verified the input artifact hash, reproduced both complete results and passed all three tests without finding a material defect.

## Research implication

Prioritize independently validated improvements to margin prediction and preserve the market comparison as a baseline requirement. Do not promote a feature because a reused development subset improves, or translate this result into a stake recommendation. Total prediction also needs further evidence; an interval crossing zero is not evidence of a competitive advantage. Production forecasts remain unchanged.
