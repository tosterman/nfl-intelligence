import { test } from 'node:test';
import assert from 'node:assert/strict';
import { matchupHealth } from '../src/lib/matchup-health';
const snapshot = {status: 'ok', season: 2026, week: 1, checkedAt: '2026-09-11T12:00:00Z',
  freshUntil: Date.parse('2026-09-11T14:00:00Z'), currentSeason: {season: 2026, week: 1, gameType: 'REG',
    cutoff: '2026-09-09', sourceObservedAt: '2026-09-11T12:01:00Z', status: 'no-eligible-games',
    gameIds: [] as string[], teams: {}, sourceSha256: 'a'.repeat(64), scheduleSha256: 'b'.repeat(64)}};

test('valid empty weekly samples are healthy, but expiry and failed collection are not', () => {
  const now = Date.parse(snapshot.currentSeason.sourceObservedAt);
  const expected = {season: snapshot.season, week: snapshot.week, gameType: 'REG'};
  assert.equal(matchupHealth(snapshot, expected, now).status, 'ok');
  for (const changed of [{...snapshot, status: 'unavailable'}, {...snapshot, freshUntil: now},
    {...snapshot, freshUntil: now + 31 * 3600000}, {...snapshot, week: snapshot.week + 1},
    {...snapshot, checkedAt: new Date(now + 1).toISOString()},
    {...snapshot, currentSeason: {...snapshot.currentSeason, sourceSha256: 'invalid'}},
    {...snapshot, currentSeason: {...snapshot.currentSeason, gameType: 'POST'}},
    ...['invalid', '2026-02-30', '2026-09-12'].map(cutoff => ({...snapshot, currentSeason: {...snapshot.currentSeason, cutoff}})),
    {...snapshot, currentSeason: {...snapshot.currentSeason, status: 'available'}}])
    assert.equal(matchupHealth(changed, expected, now).status, 'unavailable');
});
