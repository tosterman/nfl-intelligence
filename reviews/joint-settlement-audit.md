# Signed spread and total settlement audit

The fixed comparison provides no clear improvement in settlement probability quality. All four paired intervals include zero. The empirical distribution remains research-only; production cover probabilities, push probabilities, expected returns and stake advice remain disabled.

| Market / loss | Empirical | Reference | Difference | 95% week-bootstrap interval |
|---|---:|---:|---:|---|
| Spread Brier | 0.525593 | 0.527151 | -0.001558 | [-0.008071, +0.005557] |
| Spread log loss | 0.737798 | 0.735849 | +0.001950 | [-0.007530, +0.011033] |
| Total Brier | 0.502957 | 0.502509 | +0.000448 | [-0.004632, +0.005765] |
| Total log loss | 0.696232 | 0.695801 | +0.000432 | [-0.004740, +0.005825] |

Both markets include all 285 retained 2025 development records, with no missing lines. There are 71 integer spread lines and one observed push; empirical expected 3.82 pushes, reference 2.00. This sparse sample cannot establish reliable push calibration. All 285 totals are half-point lines: zero push probability is structural, so this sample supplies no total-push calibration evidence. Do not interpret zero expected and observed total pushes as successful push validation.

The line convention was traced through build_data.py and checked against [nflverse documentation](https://nflverse.r-universe.dev/nflfastR/doc/manual.html): positive spread_line means points the home team was favored by. Thus home cover is actual home margin greater than marketMargin; the displayed home handicap has the opposite sign. Probability classes are home-cover/push/home-loss or over/push/under, not win/tie/loss. Three-component Brier loss is the sum, not the average, of squared class errors.

The protocol was committed before execution. Frozen code/prior/fit identities matched, and the report retains all per-game vectors, observed classes, input fingerprints and paired uncertainty. Tests cover a known push distribution, side-swap/sign reversal, half-point impossibility of pushes, total sum arithmetic and invalid/impossible observations. All 25 joint-score tests pass. The outcomes use final schedule scores and recorded closing lines; neither bookmaker-specific settlement nor executable offers are verified. Four intervals are unadjusted and the sample is reused development data.

Independent review reproduced every settlement and all four bootstrap intervals. It found an empty-market metadata error, fixed with a regression: a market with no recorded lines now returns unknown comparison fields instead of crashing. The current complete-sample results are unchanged.
