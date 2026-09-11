import React from 'react';
import evidence from '../../data/total-explanations.json';
import type { Snapshot } from '../lib/types';
import { selectTotalExplanation } from '../lib/total-explanation';
import { signed } from '../lib/teams';

export function TotalExplanation({snapshot}: {snapshot: Snapshot}) {
  const explanation = selectTotalExplanation(evidence, snapshot);
  return <section className="panel">
    <h2 id="total-explanation" tabIndex={-1}>Why this total?</h2>
    {!explanation ? <p>A verified total breakdown is not available for this saved forecast.</p> : <>
      <p>The model starts at {explanation.baseline.toFixed(1)} combined points. Team and venue terms {explanation.adjustment >= 0 ? 'add' : 'subtract'} {Math.abs(explanation.adjustment).toFixed(1)} points, giving an expected total of <strong>{explanation.total.toFixed(1)}</strong>.</p>
      <p className="fine">The starting point combines the two fitted model intercepts; it is not the league scoring average. These terms explain the calculation, not causal effects. Personnel and weather do not adjust this total.</p>
      <details><summary>See the total calculation</summary>
        <table className="comparison"><caption>Contributions to combined points · three-decimal accounting</caption>
          <thead><tr><th scope="col">Model term</th><th scope="col">Points</th></tr></thead>
          <tbody>{explanation.terms.map(term => <tr key={term.name}><th scope="row">{term.name}</th><td>{signed(term.points, 3)}</td></tr>)}</tbody>
          <tfoot><tr><th scope="row">Expected total</th><td>{explanation.total.toFixed(3)}</td></tr></tfoot>
        </table>
        <p className="fine">75% scoring model and 25% efficiency model. Terms already include those weights. The efficiency terms use combined offensive and opponent-allowed profiles. Rounded terms include an explicit reconciliation where needed.</p>
      </details>
    </>}
  </section>;
}
