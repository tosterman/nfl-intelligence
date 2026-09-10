# Fixed key-margin and tail audit

The empirical prior better represents the football scoring concentration around three-point wins than the smooth Gaussian reference. It still underpredicts their aggregate frequency and does not establish conditional calibration. Five of the other six event Brier point estimates favor the reference; all six intervals include zero. Production remains unchanged.

| Event | Empirical expected | Reference expected | Observed | Brier difference | 95% interval |
|---|---:|---:|---:|---:|---|
| margin3 | 38.78 | 14.96 | 46 | -0.011268 | [-0.018891, -0.004474] |
| margin7 | 23.74 | 13.78 | 26 | -0.001820 | [-0.004007, +0.000446] |
| margin10 | 14.22 | 12.39 | 10 | +0.000148 | [-0.000127, +0.000396] |
| margin14 | 14.83 | 10.14 | 11 | +0.000182 | [-0.000632, +0.000909] |
| margin21plus | 57.23 | 50.67 | 51 | +0.000450 | [-0.001254, +0.002253] |
| total30orless | 40.67 | 37.64 | 39 | +0.000050 | [-0.000581, +0.000682] |
| total60plus | 48.14 | 46.97 | 47 | +0.000257 | [-0.000261, +0.000753] |

All 285 reused 2025 development forecasts are included. Lower Brier loss is better; negative differences favor empirical. Intervals resample whole weeks, are unadjusted for seven overlapping diagnostics and do not describe seven independent discoveries. Neither method was refitted. Frozen prior/code/fit checks passed. The complete report retains per-game probabilities and outcomes with input/protocol/code hashes.

Absolute three-point margin pools home and away wins. It is not the probability of a push at either signed three-point spread. The finite grid omits scores above 100 for either team, and aggregate count agreement is not evidence of accurate individual-game probabilities. Three tests verify known probability mass, side-swap symmetry, inclusive boundaries, invalid inputs and observed Brier calculations.

Next engine gate: signed-spread and push calibration plus prospective results. Do not retune this frozen shadow track to the observed event frequencies.

Independent review reproduced all 570 distributions, all seven event probabilities/Brier scores per game and all seven paired bootstrap intervals; no material defect was found. The full joint-score test group passes 21 tests.
