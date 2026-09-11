import type { WeeklyGame, WeeklySide } from './weekly-matchup';

export type PriorMatchup = { schemaVersion: number; status: string; season: number; forecastSeason: number;
  sample: string; includesPostseason: boolean; cutoff: string; sourceObservedAt: string;
  sourceSha256: string; scheduleSha256: string;
  teams: Record<string, { offense: WeeklySide; defense: WeeklySide }> };

export function selectPriorContext(data: PriorMatchup, game: WeeklyGame, now = Date.now()) {
  const cutoff = Date.parse(data.cutoff + 'T00:00:00Z');
  const observed = Date.parse(data.sourceObservedAt), kickoff = Date.parse(game.kickoff ?? '');
  if (data.schemaVersion !== 1 || data.status !== 'available' || data.sample !== 'prior-season' ||
      !data.includesPostseason || data.forecastSeason !== game.season || data.season !== game.season - 1 ||
      game.away === game.home || !Object.hasOwn(data.teams, game.away) || !Object.hasOwn(data.teams, game.home) ||
      ![cutoff, observed, kickoff, now].every(Number.isFinite) || observed > now || cutoff > observed ||
      cutoff > kickoff || new Date(cutoff).toISOString().slice(0, 10) !== data.cutoff ||
      ![data.sourceSha256, data.scheduleSha256].every(hash => /^[a-f0-9]{64}$/.test(hash))) return null;
  // Historical samples do not expire on the live feed's 30-hour schedule.
  return data;
}
