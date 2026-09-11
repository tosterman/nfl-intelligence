import { test } from 'node:test';
import assert from 'node:assert/strict';
import evidence from '../data/total-explanations.json';
import { site } from '../src/lib/data';
import { selectTotalExplanation } from '../src/lib/total-explanation';

test('total explanations match current snapshot identity and reconcile', () => {
  let checked = 0;
  for (const game of site.games.filter(g => g.snapshot)) {
    const snapshot = game.snapshot!;
    if (!Object.hasOwn(evidence.records, snapshot.hash)) continue;
    checked++;
    const value = selectTotalExplanation(evidence, snapshot);
    assert.ok(value, game.id);
    assert.ok(Math.abs(value.baseline + value.adjustment - snapshot.prediction.total) < 1e-7);
    for (const change of [{hash: '0'.repeat(64)}, {modelCodeHash: 'other'}, {gameId: 'other'},
      {prediction: {...snapshot.prediction, total: snapshot.prediction.total + 1}}])
      assert.equal(selectTotalExplanation(evidence, {...snapshot, ...change}), null);
    const row = value!;
    const tampered = {...evidence, records: {...evidence.records, [snapshot.hash]: {...row, terms: [...row.terms, {name: 'invented', points: 1}]}}};
    assert.equal(selectTotalExplanation(tampered, snapshot), null);
  }
  assert.ok(checked > 0, 'No current explanation was exercised');
});
