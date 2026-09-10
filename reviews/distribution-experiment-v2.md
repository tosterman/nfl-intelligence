# Settlement-aware distribution correction — 2026-09-10

**Recommendation: retain as a research candidate; further validation before production.** The explicit tie constraint fixes the initial model's gross tie overprediction and impossible postseason tie support. The empirical bandwidth2 shape still wins the declared log-score selection, with modest gains on the separate2023 diagnostic. This is a constrained final-margin probability approximation, **not an overtime simulator or validated NFL key-number model**.

## Prespecified correction

Postseason tie probability is exactly zero. For regular-season games, use a Beta(1,99) prior: mean1%, effective prior sample100 games. Add only completed regular-season outcomes strictly before the weekly cutoff, starting with the experiment's2017 out-of-sample record. The posterior mean is `(prior ties + 1)/(eligible games + 100)`. The prior was declared for this correction and was not searched over the evaluation data. Target-week games, future games, postseason games and incomplete outcomes are excluded.

Remove each candidate's old zero-margin mass, multiply every nonzero bin proportionally to sum to one minus the fitted tie probability, then insert that tie probability at zero. This preserves symmetry and normalization. It does not reconstruct touchdowns, field goals or possession sequences.

The same five shape candidates are compared using2021–2022 discrete negative log score. The mean prediction engine, bandwidth grid and evaluation samples remain fixed.2023 is shown separately and was already inspected in the initial experiment; it is a reused diagnostic, not a pristine holdout. No2024–2025 data are loaded or used.

## Results

| Candidate | 2021–2022 log score ↓ | CRPS ↓ | 80% coverage |
|---|---:|---:|---:|
| Constrained normal sigma14 | 3.971325 | 7.265864 | 83.66% |
| Constrained fitted normal | 3.965295 | 7.247308 | 81.90% |
| Constrained empirical bandwidth1 | 3.957751 | 7.234179 | 81.72% |
| **Constrained empirical bandwidth2** | **3.957500** | **7.235619** | **81.90%** |
| Constrained empirical bandwidth4 | 3.963093 | 7.245166 | 83.13% |

The selected bandwidth2 method has2023 log score **3.991352** versus **4.002718** for the constrained normal reference; CRPS **7.560602** versus **7.581718**. Its80% coverage is **78.60%**, versus81.40% for the normal reference. Its three-outcome Brier remains slightly worse in2023: **0.459422** versus **0.459009**. Therefore, the modest log-score improvement does not imply every probability criterion improves.

Tie mass is shared across shape candidates by construction. Expected2021–2022 ties are **2.4657 versus3 observed**, instead of the initial empirical model's17.3448. Expected2023 ties are **1.2143 versus0 observed**, instead of8.6755. These small event counts are insufficient to establish conditional tie calibration. The pooled prior does not condition on team strength, close-game likelihood, historical overtime rule changes, or game context.

## Remaining integration gaps

- Proportional redistribution of zero-margin mass changes the distribution's mean. Do not retain the original expected margin/score and imply it exactly equals the constrained distribution's moments. A production design must explicitly reconcile that arithmetic or label the fixed mean as the location parameter rather than the resulting expectation.
- A low aggregate tie frequency and zero postseason tie mass do not validate probabilities at3,7,10 or pushes against integer market lines. No key-number calibration claim is supported here.
- The underlying residual law is pooled and symmetric; conditional variance, tail calibration, season-type differences and dependence between margin/total remain unmodeled.
- Coverage declines below80% in the separate2023 check, and the sample has been reused after review. Forward validation remains necessary.

## Evidence and implementation

Initial evidence is preserved in `reviews/distribution-experiment.md` and `reviews/distribution-experiment-results.json`. The new full results are in `reviews/distribution-experiment-v2-results.json`. `scripts/experiment_distribution.py` now uses **only NumPy and Python math.erf**, removing the initial SciPy dependency. No new research dependency or CI install change is required.

Seven tests pass: probability normalization and symmetry, zero-mean outcome consistency, proper-score sanity, future residual exclusion, zero postseason tie mass, prior-only completed-game tie fitting, and normal CDF reference values. Tests also verify incomplete outcomes cannot become ties and redistribution preserves symmetry. No production engine, ledger, site or workflow files were changed.

The original report's primary-source scoring-rule reference and NFL postseason-rule source remain applicable. Mathematical mass constraints correct a known support defect; they do not close the founding football-simulation requirement.
