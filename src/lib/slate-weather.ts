import { weatherStatus, type WeatherRecord } from "./weather";

export type SlateWeather = { text: string; expiresAt: number | null };

/** Compact display evidence; the detailed page retains source attribution. */
export function slateWeather(
  record: WeatherRecord | undefined,
  game: { kickoff: string | null; venue: string },
  now: number,
): SlateWeather {
  const status = weatherStatus(record, game, now);
  if (status !== "available" || !record)
    return { text: status, expiresAt: null };
  const parts: string[] = [];
  if (Number.isFinite(record.temperature) && ["F", "C"].includes(record.temperatureUnit ?? ""))
    parts.push(`${record.temperature}°${record.temperatureUnit}`);
  if (record.windSpeed) parts.push(`Wind ${record.windSpeed}`);
  if (Number.isFinite(record.precipitationProbability) && record.precipitationProbability! >= 0 && record.precipitationProbability! <= 100)
    parts.push(`${record.precipitationProbability}% precipitation`);
  return {
    text: parts.join(" · ") || "Forecast measurements unavailable",
    expiresAt: Math.min(Date.parse(record.issuedAt!), Date.parse(record.retrievedAt!)) + 30 * 3600000 + 1,
  };
}
