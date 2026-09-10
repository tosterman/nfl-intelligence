export type WeatherRecord = {
  status: string;
  reason?: string;
  kickoff: string | null;
  venue: string;
  issuedAt?: string;
  retrievedAt?: string;
  periodStart?: string;
  periodEnd?: string;
  temperature?: number | null;
  temperatureUnit?: string;
  precipitationProbability?: number | null;
  windSpeed?: string | null;
  windDirection?: string | null;
  summary?: string | null;
  sourceUrl?: string;
  sourceHash?: string;
};
export function weatherStatus(
  record: WeatherRecord | undefined,
  game: { kickoff: string | null; venue: string },
  now = Date.now(),
) {
  if (!record || record.status !== "available")
    return record?.reason ?? "Verified venue forecast unavailable";
  if (record.kickoff !== game.kickoff || record.venue !== game.venue)
    return "Schedule changed; forecast needs refreshing";
  const ages = [record.issuedAt, record.retrievedAt].map(
    (t) => now - Date.parse(t ?? ""),
  );
  if (
    ages.some(
      (age) => !Number.isFinite(age) || age < -300000 || age > 30 * 3600000,
    )
  )
    return "Weather forecast is outdated; awaiting refresh";
  const kickoff = Date.parse(game.kickoff ?? "");
  if (!(
    Date.parse(record.periodStart ?? "") <= kickoff &&
    kickoff < Date.parse(record.periodEnd ?? "")
  ))
    return "Kickoff-hour forecast unavailable";
  return "available";
}
