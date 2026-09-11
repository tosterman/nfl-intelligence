import type { Game } from './types';
import type { PersonnelEvidence } from './personnel-evidence';
import { personnelForGame } from './personnel';
import { personnelChangesForGame } from './personnel-changes';
import { weatherHistoryForGame, type WeatherHistory } from './weather-history';
import { weatherStatus, type WeatherRecord } from './weather';

export type ContextBrief = { gameId: string; kind: 'personnel' | 'weather'; text: string;
  previousAt: string; currentAt: string; expiresAt: number };

export function personnelBrief(evidence: PersonnelEvidence | null, game: Game, now: number): ContextBrief | null {
  if (!evidence || evidence.collection.status !== 'ok') return null;
  const current = personnelForGame(evidence.snapshot, game, now);
  const comparison = personnelChangesForGame(evidence.history, evidence.snapshot, game);
  if (current.reason || !comparison) return null;
  const changes = comparison.changes.filter(c => c.kind !== 'changed' ||
    Object.values(c.fields).some(f => f.before !== f.after));
  if (!changes.length) return null;
  const removed = changes.filter(c => c.kind === 'no-longer-present').length;
  return { gameId: game.id, kind: 'personnel',
    text: `${changes.length} player ${changes.length === 1 ? 'entry changed' : 'entries changed'} between collections.${removed ? ` ${removed} no longer in the source file; this does not establish recovery or availability.` : ''}`,
    previousAt: comparison.start, currentAt: comparison.end, expiresAt: current.expiresAt };
}

export function weatherBrief(history: WeatherHistory, record: WeatherRecord | undefined, game: Game, now: number): ContextBrief | null {
  const kickoff = Date.parse(game.kickoff ?? '');
  if (game.status === 'final' || !Number.isFinite(kickoff) || now >= kickoff ||
    weatherStatus(record, game, now) !== 'available' || !record ||
    Date.parse(record.issuedAt!) > now || Date.parse(record.retrievedAt!) > now) return null;
  const comparison = weatherHistoryForGame(history, record, game);
  if (!comparison?.changed) return null;
  const [current, previous] = comparison.issues;
  const changed:string[]=[];
  const value=(v:unknown)=>v===null||v===undefined||v===''?'Unavailable':String(v);
  const temperature=(r:WeatherRecord)=>r.temperature===null||r.temperature===undefined?'Unavailable':`${r.temperature}°${r.temperatureUnit??' (unit unknown)'}`;
  if((current.temperature??null)!==(previous.temperature??null)||(current.temperatureUnit??null)!==(previous.temperatureUnit??null))
    changed.push(`Temperature ${temperature(previous)} → ${temperature(current)}`);
  if((current.windSpeed??null)!==(previous.windSpeed??null))
    changed.push(`Wind ${value(previous.windSpeed)} → ${value(current.windSpeed)}`);
  if((current.windDirection??null)!==(previous.windDirection??null))
    changed.push(`Wind direction ${value(previous.windDirection)} → ${value(current.windDirection)}`);
  const precipitation=(v:number|null|undefined)=>v===null||v===undefined?'Unavailable':`${v}%`;
  if((current.precipitationProbability??null)!==(previous.precipitationProbability??null))
    changed.push(`Precipitation chance ${precipitation(previous.precipitationProbability)} → ${precipitation(current.precipitationProbability)}`);
  if((current.summary??null)!==(previous.summary??null))changed.push('Forecast description changed; see game evidence');
  return { gameId: game.id, kind: 'weather', text: `Outside stadium: ${changed.join(' · ')}. Field and roof conditions are unknown.`,
    previousAt: previous.issuedAt!, currentAt: current.issuedAt!,
    expiresAt: Math.min(kickoff, Date.parse(record.issuedAt!) + 30 * 3600000, Date.parse(record.retrievedAt!) + 30 * 3600000) };
}
