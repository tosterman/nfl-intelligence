import type { WeatherRecord } from "./weather";
export type WeatherObservation = WeatherRecord & { gameId: string; hash: string; locationHash: string };
export type WeatherHistory = { schemaVersion: number; records: WeatherObservation[] };
const values = (r: WeatherRecord) => JSON.stringify([r.temperature ?? null, r.temperatureUnit ?? null,
  r.windSpeed ?? null, r.windDirection ?? null, r.precipitationProbability ?? null, r.summary ?? null]);

export function weatherHistoryForGame(history: WeatherHistory, current: WeatherRecord | undefined,
  game: { id: string; venue: string; kickoff: string | null }) {
  if (history.schemaVersion !== 1 || !current || current.status !== "available" ||
    current.venue !== game.venue || current.kickoff !== game.kickoff) return null;
  const anchor = history.records.find(r => r.gameId === game.id && r.sourceHash === current.sourceHash &&
    r.retrievedAt === current.retrievedAt && r.issuedAt === current.issuedAt && r.venue === game.venue &&
    r.kickoff === game.kickoff && values(r) === values(current));
  if (!anchor) return null;
  const rows = history.records.filter(r => r.gameId === game.id && r.venue === game.venue &&
    r.kickoff === game.kickoff && r.locationHash === anchor.locationHash &&
    Date.parse(r.issuedAt!) <= Date.parse(anchor.issuedAt!) &&
    Date.parse(r.retrievedAt!) <= Date.parse(anchor.retrievedAt!))
    .sort((a, b) => Date.parse(a.retrievedAt!) - Date.parse(b.retrievedAt!));
  const issues = new Map<number, WeatherObservation>();
  for (const row of rows) {
    const issued = Date.parse(row.issuedAt!);
    const previous = issues.get(issued);
    if (previous && values(previous) !== values(row)) return null;
    issues.set(issued, row);
  }
  const result = [...issues.values()].sort((a, b) => Date.parse(b.issuedAt!) - Date.parse(a.issuedAt!));
  return { issues: result, changed: result.length > 1 && values(result[0]) !== values(result[1]) };
}
