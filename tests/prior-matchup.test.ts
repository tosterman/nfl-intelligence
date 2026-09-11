import { test } from 'node:test';
import assert from 'node:assert/strict';
import evidence from '../data/prior-matchup-context.json';
import big from '../data/explosive-plays.json';
import red from '../data/red-zone.json';
import { selectPriorContext } from '../src/lib/prior-matchup';

const game = { away: 'BUF', home: 'NYJ', season: 2026, kickoff: '2026-09-15T00:00:00Z' };
const now = Date.parse('2026-09-15T00:00:00Z');
test('prior context requires matching season, teams, source identity and valid dates', () => {
  assert.ok(selectPriorContext(evidence, game, now));
  for (const change of [{season: 2027}, {home: 'BUF'}, {home: 'UNKNOWN'}, {kickoff: null}, {kickoff: '2026-09-01'}])
    assert.equal(selectPriorContext(evidence, {...game, ...change}, now), null);
  for (const change of [{forecastSeason: 2027}, {sample: 'weekly'}, {includesPostseason: false},
    {sourceSha256: ''}, {cutoff: '2026-02-30'}, {sourceObservedAt: '2026-09-16T00:00:00Z'}])
    assert.equal(selectPriorContext({...evidence, ...change}, game, now), null);
  assert.ok(selectPriorContext(evidence, game, now + 90 * 86400000));
  const next = {...evidence, season: 2026, forecastSeason: 2027,
    cutoff: '2027-09-09', sourceObservedAt: '2027-09-10T00:00:00Z'};
  assert.ok(selectPriorContext(next, {...game, season: 2027, kickoff: '2027-09-15T00:00:00Z'}, Date.parse('2027-09-11T00:00:00Z')));
});

test('new panel source preserves every historical count', () => {
  for (const team of Object.keys(evidence.teams) as (keyof typeof evidence.teams)[]) {
    for (const side of ['offense', 'defense'] as const) {
      for (const kind of ['passing', 'rushing'] as const)
        assert.deepEqual(evidence.teams[team][side][kind], big.teams[team][side][kind]);
      assert.deepEqual(evidence.teams[team][side].inside20, red.teams[team][side]);
    }
  }
});
