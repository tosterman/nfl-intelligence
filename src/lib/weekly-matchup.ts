export type WeeklySide = { gameIds: string[]; passing: { plays: number; explosive: number };
  rushing: { plays: number; explosive: number }; inside20: { possessions: number; touchdowns: number } };
export type WeeklySnapshot = { status: string; season: number; week: number; freshUntil?: number;
  currentSeason?: { season: number; week: number; gameType: string; cutoff: string; sourceObservedAt: string;
    status: string; teams: Record<string, { offense: WeeklySide; defense: WeeklySide }> } };
export type WeeklyGame = { away: string; home: string; season: number; week?: number; type?: string; kickoff: string | null };

export function selectWeeklyContext(snapshot: WeeklySnapshot, game: WeeklyGame, now = Date.now()) {
  const data = snapshot.currentSeason;
  const phase = ['WC', 'DIV', 'CON', 'SB'].includes(game.type ?? '') ? 'POST' : game.type;
  const unavailable = (reason: string) => ({ reason, data: null, expiresAt: 0 });
  if (snapshot.status !== 'ok' || !data || snapshot.season !== game.season || snapshot.week !== game.week ||
      data.season !== game.season || data.week !== game.week || data.gameType !== phase || game.away === game.home)
    return unavailable('Current-season evidence is not available for this week.');
  const observed = Date.parse(data.sourceObservedAt), cutoff = Date.parse(data.cutoff + 'T00:00:00Z');
  const kickoff = Date.parse(game.kickoff ?? '');
  const expiresAt = snapshot.freshUntil ?? NaN;
  if (![now, observed, cutoff, kickoff, expiresAt].every(Number.isFinite) || observed > now ||
      cutoff > kickoff || cutoff > observed || cutoff > now || new Date(cutoff).toISOString().slice(0, 10) !== data.cutoff || now >= expiresAt || expiresAt > observed + 30 * 3600000)
    return unavailable('Current-season evidence is awaiting a verified refresh.');
  if (data.status === 'no-eligible-games')
    return { reason: 'No earlier games from this season qualify for this week’s sample.', data: null, expiresAt };
  if (data.status !== 'available' || !Object.hasOwn(data.teams, game.away) || !Object.hasOwn(data.teams, game.home))
    return unavailable('Both teams do not yet have a complete current-season sample.');
  return { reason: null, data, expiresAt };
}
