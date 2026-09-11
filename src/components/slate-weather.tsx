"use client";
import type { SlateWeather } from "@/lib/slate-weather";
import { useClock } from "./market-panel";

export function SlateWeatherContext({ weather, kickoff, initialNow }: {
  weather: SlateWeather; kickoff: string | null; initialNow: number;
}) {
  const kickoffAt = Date.parse(kickoff ?? "");
  const now = useClock(initialNow, [kickoffAt, weather.expiresAt ?? NaN]);
  // The slate is a forward-looking forecast; do not present it as observed weather.
  if (!Number.isFinite(kickoffAt) || now >= kickoffAt) return null;
  const expired = weather.expiresAt !== null && now >= weather.expiresAt;
  return <div className="slate-weather">
    <small>Kickoff weather · Outside stadium</small>
    <p>{expired ? "Weather forecast is outdated; awaiting refresh" : weather.text}</p>
    {weather.expiresAt !== null && !expired && <small>NWS · Field / roof conditions unknown · Context only</small>}
  </div>;
}
