# Fixed margin-scale diagnostic: do not promote

The protocol was committed as `7b9c104` before execution. A zero-intercept, nonnegative least-squares coefficient fitted to 285 games from 2024 was **1.239313**. Applying that frozen coefficient to all 285 games from 2025 made the primary mean absolute margin error slightly worse.

| 2025 diagnostic | Unchanged baseline | Scale correction |
|---|---:|---:|
| Margin MAE | 10.165389 | 10.216417 |
| Margin RMSE | 12.934311 | 12.925298 |

Candidate minus baseline MAE is **+0.051027** points, with a whole-week resampled 95% interval of **-0.121691 to +0.220249**. A tiny secondary RMSE improvement does not override the declared primary objective. The interval is compatible with both improvement and harm; this is not proof that all forms of calibration fail. It is insufficient evidence to add this correction.

The unchanged closing-market benchmark on the same 285 games has margin MAE 9.670175. No market information was used in fitting the scale. The remaining margin gap therefore is not resolved by this simple uniform expansion.

Training and evaluation seasons are disjoint. The latest training outcome's 24-hour embargo ends February 10, 2025 at 23:30 UTC; first evaluation kickoff is September 5, 2025 at 00:20 UTC. Fingerprints preserve the exact published performance artifact, schedule used for the timing check, protocol and calculation code. The JSON retains all evaluation predictions and outcomes. Base forecasts were read as published; no base-model refit or production mutation occurred.

Three tests pass: a known exact scale and side-swap symmetry, later-outcome poisoning that cannot change the fitted coefficient, and rejection of degenerate/nonfinite training values with the declared nonnegative boundary. Existing benchmark tests cover the paired whole-week resampling. These are reused development seasons, not an untouched holdout; cross-week dependence and model-selection uncertainty are not included in the interval. No probability, interval, exact-score or expected-return improvement is claimed.

Keep the baseline unchanged. Further improvements should address missing football information or independently justified structure, followed by new-data validation; do not search additional scale choices on this evaluation season.

Independent review verified artifact/protocol hashes, reproduced the complete result and passed all three tests. It found no material defect and confirmed that rejecting promotion does not amount to proof of genuine deterioration.
