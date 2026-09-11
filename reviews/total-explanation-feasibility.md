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

Current artifact generation, immutable explanation retention, release integration
and the user-facing total explanation remain unfinished.
