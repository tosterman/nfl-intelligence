import type { PersonnelSnapshot, PlayerReport } from './personnel';
import { teams } from './teams';
type Row = Record<string, unknown>;
const object = (v: unknown): Row | null => v !== null && typeof v === 'object' && !Array.isArray(v) ? v as Row : null;
const hash = (v: unknown) => typeof v === 'string' && /^[a-f0-9]{64}$/.test(v);

export function seasonParticipation(raw: unknown, snapshot: PersonnelSnapshot, player: PlayerReport, now = Date.now()) {
  const data = object(raw);
  if (!data || data.schemaVersion !== 1 || data.sourceSeason !== player.season ||
      data.personnelSourceHash !== snapshot.sourceHash || data.personnelRetrievedAt !== snapshot.retrievedAt ||
      !hash(data.sourceHash) || !Array.isArray(data.records) || !['current','retained'].includes(String(data.collectionStatus))) return null;
  const acquired = Date.parse(String(data.sourceRetrievedAt)), calculated = Date.parse(String(data.calculatedAt)), reported = Date.parse(snapshot.retrievedAt);
  if (![acquired, calculated, reported, now].every(Number.isFinite) || acquired > calculated || reported > calculated || calculated > now) return null;
  const matches = data.records.map(object).filter(r => r && ['playerId','team','season','type','week','name'].every(k => r[k] === player[k as keyof PlayerReport]));
  if (matches.length !== 1 || matches[0]!.identityStatus !== 'matched') return null;
  const record = matches[0]!, usage = object(record.usage), cutoff = Date.parse(String(record.cutoff));
  if (!usage || !Number.isFinite(cutoff) || cutoff > Math.min(acquired, reported) || usage.cutoff !== record.cutoff ||
      usage.season !== player.season || usage.week !== player.week || usage.type !== player.type) return null;
  const overall = object(usage.overall);
  if (!overall || !['available','unavailable'].includes(String(overall.status))) return null;
  const context = {season: player.season, sourceRetrievedAt: String(data.sourceRetrievedAt), retained: data.collectionStatus === 'retained', cutoff: String(record.cutoff)};
  if (overall.status === 'unavailable') return {...context, appearances: null, shares: null, lastAppearance: null, currentTeamAppearances: 0, formerTeamAppearances: 0};
  const shares = object(overall.weightedShares), games = overall.games;
  if (!shares || !Array.isArray(games) || !Number.isInteger(overall.appearances) || Number(overall.appearances) < 1 || Number(overall.appearances) > 8 || games.length !== overall.appearances) return null;
  for (const k of ['offense_pct','defense_pct','st_pct']) if (typeof shares[k] !== 'number' || !Number.isFinite(shares[k]) || Number(shares[k]) < 0 || Number(shares[k]) > 1) return null;
  const rows = games.map(object);
  if (rows.some(g => !g || typeof g.gameId !== 'string' || !Object.hasOwn(teams, String(g.team)) || !Number.isFinite(Date.parse(String(g.kickoff))) || Date.parse(String(g.kickoff)) + 86400000 >= cutoff) || new Set(rows.map(g => g!.gameId)).size !== rows.length) return null;
  const latest = Math.max(...rows.map(g => Date.parse(String(g!.kickoff))));
  if (Date.parse(String(overall.lastAppearance)) !== latest) return null;
  return {...context, appearances: Number(overall.appearances), shares: {offense: Number(shares.offense_pct), defense: Number(shares.defense_pct), specialTeams: Number(shares.st_pct)},
    lastAppearance: String(overall.lastAppearance), currentTeamAppearances: rows.filter(g => g!.team === player.team).length,
    formerTeamAppearances: rows.filter(g => g!.team !== player.team).length};
}
