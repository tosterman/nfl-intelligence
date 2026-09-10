import { weatherStatus, type WeatherRecord } from "./weather";

type Game = {
  id: string;
  kickoff: string | null;
  venue: string;
  neutral?: boolean;
};
type Venue = { [key: string]: unknown; latitude?: number; longitude?: number };

export function weatherHealth(
  snapshot: {
    collectionStartedAt: string;
    generatedAt: string;
    games: Record<string, WeatherRecord>;
  },
  games: Game[],
  venues: Record<string, Venue>,
  now = Date.now(),
) {
  const generated = Date.parse(snapshot.generatedAt);
  const started = Date.parse(snapshot.collectionStartedAt);
  const fresh =
    Number.isFinite(generated) &&
    Number.isFinite(started) &&
    started <= generated &&
    generated <= now &&
    now - started < 30 * 3600000;
  // Match the collector's window at acquisition, excluding games already kicked off.
  // A game entering the seven-day window between daily collections is not a failure.
  const eligible = games.filter((game) => {
    const kickoff = Date.parse(game.kickoff ?? "");
    const venue = venues[game.venue];
    return (
      kickoff > now &&
      kickoff > started &&
      kickoff - started <= 7 * 86400000 &&
      !game.neutral &&
      typeof venue?.latitude === "number" &&
      Number.isFinite(venue.latitude) &&
      Math.abs(venue.latitude) <= 90 &&
      typeof venue.longitude === "number" &&
      Number.isFinite(venue.longitude) &&
      Math.abs(venue.longitude) <= 180
    );
  });
  const checks = eligible.map((game) => {
    const record = snapshot.games[game.id];
    const valid =
      weatherStatus(record, game, now) === "available" &&
      /^[a-f0-9]{64}$/.test(record?.sourceHash ?? "");
    return {
      gameId: game.id,
      status: valid ? "ok" : "unavailable",
      issuedAt: record?.issuedAt ?? null,
      retrievedAt: record?.retrievedAt ?? null,
      sourceHash: record?.sourceHash ?? null,
    };
  });
  return {
    status:
      fresh && checks.every((check) => check.status === "ok")
        ? "ok"
        : "unavailable",
    collectionStartedAt: snapshot.collectionStartedAt,
    generatedAt: snapshot.generatedAt,
    maximumAgeHours: 30,
    eligibleGames: checks.length,
    availableGames: checks.filter((check) => check.status === "ok").length,
    checks,
    scope:
      "Unplayed games with verified US coordinates inside the collection-time seven-day window. Zero eligible games is valid; this does not establish complete venue coverage or a weather adjustment to the model.",
  };
}
