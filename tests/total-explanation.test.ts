import { test } from 'node:test';
import assert from 'node:assert/strict';
import evidence from '../data/total-explanation-archive/187b903b528dc2e39bc1ce5b92c4a3ec3d545bcf778f8f8bc3278f4c621519c0.json';
import type { Snapshot } from '../src/lib/types';
import { selectTotalExplanation } from '../src/lib/total-explanation';

test('total explanations match saved snapshot identity and reconcile', () => {
  let checked = 0;
  for (const [identity, row] of Object.entries(evidence.records)) {
    const snapshot = {hash: identity, gameId: row.gameId, modelCodeHash: evidence.modelCodeHash,
      prediction: {total: row.total}} as Snapshot;
    checked++;
    const value = selectTotalExplanation(evidence, snapshot);
    assert.ok(value, row.gameId);
    assert.ok(Math.abs(value.baseline + value.adjustment - snapshot.prediction.total) < 1e-7);
    for (const change of [{hash: '0'.repeat(64)}, {modelCodeHash: 'other'}, {gameId: 'other'},
      {prediction: {...snapshot.prediction, total: snapshot.prediction.total + 1}}])
      assert.equal(selectTotalExplanation(evidence, {...snapshot, ...change}), null);
    const tampered = {...evidence, records: {...evidence.records, [snapshot.hash]: {...value!, terms: [...value!.terms, {name: 'invented', points: 1}]}}};
    assert.equal(selectTotalExplanation(tampered, snapshot), null);
  }
  assert.ok(checked > 0, 'No current explanation was exercised');
  assert.equal(selectTotalExplanation({...evidence, records: {}}, {hash: '0'.repeat(64)} as Snapshot), null);
});
