import type { WeeklySnapshot } from './weekly-matchup';
type Snapshot = WeeklySnapshot & { checkedAt: string; currentSeason?: NonNullable<WeeklySnapshot['currentSeason']> & {
  gameIds: string[]; sourceSha256: string; scheduleSha256: string;
} };
export function matchupHealth(snapshot: Snapshot, expected: {season: number; week: number; gameType: string}, now = Date.now()) {
  const data = snapshot.currentSeason;
  const checked = Date.parse(snapshot.checkedAt), observed = Date.parse(data?.sourceObservedAt ?? '');
  const expires = snapshot.freshUntil ?? NaN;
  const cutoff = Date.parse((data?.cutoff ?? '') + 'T00:00:00Z');
  const ids = data?.gameIds ?? [];
  const valid = snapshot.status === 'ok' && data && snapshot.season === expected.season && snapshot.week === expected.week &&
    data.season === expected.season && data.week === expected.week && ['REG', 'POST'].includes(expected.gameType) && data.gameType === expected.gameType &&
    Number.isFinite(cutoff) && new Date(cutoff).toISOString().slice(0, 10) === data.cutoff && cutoff <= observed &&
    /^[a-f0-9]{64}$/.test(data.sourceSha256) && /^[a-f0-9]{64}$/.test(data.scheduleSha256) &&
    ids.every(id => typeof id === 'string' && id.length > 0) && new Set(ids).size === ids.length &&
    ((data.status === 'no-eligible-games' && ids.length === 0) || (data.status === 'available' && ids.length > 0));
  const fresh = [now, checked, observed, expires].every(Number.isFinite) && checked <= observed && observed <= now &&
    now - checked < 30 * 3600000 && expires > now && expires <= observed + 30 * 3600000;
  return { status: valid && fresh ? 'ok' : 'unavailable', season: snapshot.season, week: snapshot.week,
    expectedSeason: expected.season, expectedWeek: expected.week, gameType: data?.gameType ?? null, expectedGameType: expected.gameType, checkedAt: snapshot.checkedAt,
    cutoff: data?.cutoff ?? null, sourceObservedAt: data?.sourceObservedAt ?? null, expiresAt: Number.isFinite(expires) ? new Date(expires).toISOString() : null,
    sourceHash: data?.sourceSha256 ?? null, scheduleHash: data?.scheduleSha256 ?? null,
    sampleStatus: data?.status ?? 'unavailable', gameCount: ids.length, maximumAgeHours: 30,
    scope: 'Current weekly collection and retained source freshness. No claim of predictive accuracy or complete historical data availability.' };
}
