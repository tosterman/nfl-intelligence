# Fixed spread/total settlement diagnostic

Evaluate the unchanged empirical and Gaussian-reference joint distributions on all retained 2025 development forecasts with a recorded market line. Reuse the frozen 2010–2023 prior, score grid, mean constraints and tie policy from the joint-score evaluation; enforce its prior/code/fit identities. Missing lines are explicitly counted, never imputed. Invalid lines fail. Lines must be finite half-point increments.

The archive's `marketMargin` is the home winning margin implied by the market, the negative of the displayed home handicap. For margin M and archive line L: home cover if M>L, push if M=L, loss if M<L. For total T and marketTotal U: over if T>U, push if T=U, under if T<U. Include all final points in the retained schedule; no claim is made about a particular sportsbook's overtime/settlement rules.

For spread and total separately, report the three-outcome probability vector, observed class, sum-of-three-components Brier loss and negative log probability of the observed class for every eligible game. Report mean losses, expected versus observed pushes, and integer-line and half-point-line sample counts. Both priors use exactly the same sample. Impossible observed classes or zero observed probability fail without clipping.

Use paired, whole-week bootstrap differences (empirical minus reference), 10,000 draws, seed 20260910, separately for Brier and log loss. Four intervals are descriptive and unadjusted for multiple comparisons. No favorable-line or betting-selection subset, ROI calculation, stake sizing, tuning or production promotion. These are retrospective comparisons at recorded closing-market lines, not executable pregame offers, bookmaker-calibrated probabilities or prospective validation.
