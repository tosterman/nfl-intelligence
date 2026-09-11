# Explaining projected totals

Independent code review and direct formula inspection establish an additive
accounting route without changing the frozen numerical engine:

- Scoring total: twice the scoring intercept plus both offensive coefficients
  and both defensive coefficients. Home-field terms cancel in the sum.
- Efficiency total: raw-coordinate intercept, venue coefficient and fourteen
  summed-feature products. Returned coefficients already incorporate training
  centering/scaling; do not center inputs a second time.
- Blend: 75% scoring total plus 25% efficiency total, rounded to three decimals.

`scripts/total_explanation.py` implements this accounting separately. Its terms
distinguish the efficiency intercept from league scoring. It requires the fixed
design, finite inputs, team identities and exact rounded-total agreement.
Displayed rounding is explicitly reconciled. No snapshot or engine file changed.

Two deterministic synthetic tests pass against direct matrix calculations,
including side swaps, cancellation of scoring home field, zero neutral efficiency
venue contribution, and rejection of an unsupported design or mismatched total.
This proves algebraic behavior only, not current-forecast reconstruction.

Before UI display, a separate replay builder must verify retained inputs and
engine/configuration identity, reproduce the complete archived prediction using
the unchanged fitting methods, then bind the explanation to its snapshot hash,
input manifest and explanation-code hash. Current snapshots contain margin
contributions but lack total coefficients; those cannot be inferred from margin
differences. Recomputing the existing fit is required. This is explanatory replay,
not model selection or evidence of improved predictive accuracy.

`scripts/build_total_explanations.py` now reproduces the complete current
prediction objects before generating separate review explanations. It admits
only the reviewed engine hash, rechecks input bytes after fitting, and binds
each explanation to the snapshot hash and the report to the edition, engine and
explanation code. The formulas use the unchanged engine's fit functions and
feature builder with the fixed parameters.

The actual retained edition produced 15 exact forecast matches and 15 reconciled
total explanations in `reviews/total-explanations-replay.json`. Two additional
tests passed: rejecting failed/unreviewed replay, and actual current replay with
byte preservation of site, ledger and all three production engine files. The
separately frozen joint-model files also retained their expected hashes.

For ATL/PIT the saved total is 44.770. The decomposition includes distinct
scoring and efficiency intercepts, scoring offense/defense, efficiency venue and
fourteen efficiency sum terms, with an explicit 0.001 rounding reconciliation.
These are algebraic contributions, not estimates of causal football effects.

Immutable explanation retention, input-manifest linkage, release integration
and user-facing display remain unfinished. This review output is not imported
by the app and does not change existing forecasts.
