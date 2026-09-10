# Joint-score event diagnostic protocol

Run descriptive diagnostics on the same 285 reused 2025 development forecasts as the fixed joint-score evaluation. Retain its frozen 2010–2023 priors, score grid, point means, solver and regular/postseason tie policy. Verify frozen prior/code/fit identities before evaluation. Do not tune or promote the model based on this audit.

Before execution, fix these events: absolute winning margin exactly 3, 7, 10 and 14; absolute margin at least 21; total score at most 30; total score at least 60. These are overlapping diagnostics, not an exhaustive partition. Absolute margins pool both winners and do not estimate push risk for a particular signed spread.

For each event and both empirical/reference distributions, retain every game's probability, observed binary outcome and Brier loss. Report expected count, observed count, mean probability, observed frequency and mean Brier. Report paired empirical-minus-reference Brier differences with 10,000 whole-week bootstrap draws (seed 20260910), using the existing season-stratified comparison helper. Intervals are descriptive and unadjusted for seven comparisons. Positive differences favor the reference. No post-result choice of event thresholds or subset is permitted.

Finite-grid tail probabilities omit outcomes beyond 100 points per team. Aggregate expected/observed agreement is not conditional calibration, and a rare-event Brier improvement can reward low probabilities. This is not proof of profitable betting, a settlement model or independent prospective validation. Keep production unchanged and record all data/code fingerprints.
