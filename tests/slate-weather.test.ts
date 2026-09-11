import { test } from "node:test";
import assert from "node:assert/strict";
import { slateWeather } from "../src/lib/slate-weather";
import type { WeatherRecord } from "../src/lib/weather";

const now = Date.parse("2026-09-11T12:00:00Z");
const game = { venue: "Venue", kickoff: "2026-09-13T17:00:00Z" };
const record: WeatherRecord = { ...game, status: "available",
  issuedAt: "2026-09-11T10:00:00Z", retrievedAt: "2026-09-11T11:00:00Z",
  periodStart: game.kickoff, periodEnd: "2026-09-13T18:00:00Z",
  temperature: 0, temperatureUnit: "F", windSpeed: "5 to 10 mph", precipitationProbability: 0 };

test("slate weather preserves zero values and the inclusive freshness boundary", () => {
  const summary = slateWeather(record, game, now);
  assert.equal(summary.text, "0°F · Wind 5 to 10 mph · 0% precipitation");
  assert.equal(summary.expiresAt, Date.parse(record.issuedAt!) + 30 * 3600000 + 1);
  assert.equal(slateWeather(record, game, summary.expiresAt! - 1).expiresAt, summary.expiresAt);
  assert.equal(slateWeather(record, game, summary.expiresAt!).expiresAt, null);
});
test("slate rejects stale, missing and rescheduled evidence without temperatures", () => {
  for (const summary of [slateWeather(undefined, game, now),
    slateWeather(record, { ...game, venue: "Other" }, now),
    slateWeather(record, { ...game, kickoff: "2026-09-13T18:00:00Z" }, now),
    slateWeather(record, game, now + 31 * 3600000)]) {
    assert.equal(summary.expiresAt, null);
    assert.ok(!summary.text.includes("°F"));
  }
});
test("invalid measurements cannot become slate weather values", () => {
  const summary = slateWeather({ ...record, temperature: NaN, windSpeed: null,
    precipitationProbability: 101 }, game, now);
  assert.equal(summary.text, "Forecast measurements unavailable");
});
