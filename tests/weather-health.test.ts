import { test } from "node:test";
import assert from "node:assert/strict";
import { weatherHealth } from "../src/lib/weather-health";
import type { WeatherRecord } from "../src/lib/weather";
const at = "2026-09-10T12:00:00Z",
  now = Date.parse(at);
const game = { id: "g", venue: "Venue", kickoff: "2026-09-11T12:00:00Z" };
const venues = { Venue: { latitude: 40, longitude: -75 } };
const record = {
  ...game,
  status: "available",
  issuedAt: at,
  retrievedAt: at,
  periodStart: game.kickoff,
  periodEnd: "2026-09-11T13:00:00Z",
  sourceHash: "a".repeat(64),
};
const snapshot = {
  collectionStartedAt: at,
  generatedAt: at,
  games: { g: record },
};
test("weather health detects a failed eligible forecast and stale sources", () => {
  assert.equal(weatherHealth(snapshot, [game], venues, now).status, "ok");
  const variants: Record<string, WeatherRecord>[] = [
    {},
    { g: { ...record, status: "unavailable" } },
    { g: { ...record, issuedAt: "2026-09-08T12:00:00Z" } },
    { g: { ...record, sourceHash: "" } },
  ];
  for (const games of variants) {
    assert.equal(
      weatherHealth({ ...snapshot, games }, [game], venues, now).status,
      "unavailable",
    );
  }
});
test("no eligible games is healthy only with fresh collection", () => {
  for (const games of [
    [],
    [{ ...game, neutral: true }],
    [{ ...game, venue: "Unknown" }],
    [{ ...game, kickoff: "2026-09-10T11:00:00Z" }],
    [{ ...game, kickoff: "2026-09-18T12:00:00Z" }],
  ]) {
    const result = weatherHealth(snapshot, games, venues, now);
    assert.equal(result.status, "ok");
    assert.equal(result.eligibleGames, 0);
    assert.equal(
      weatherHealth({ ...snapshot, generatedAt: "invalid" }, games, venues, now)
        .status,
      "unavailable",
    );
  }
});
test("schedule changes and aged collections cannot report healthy", () => {
  assert.equal(
    weatherHealth(
      snapshot,
      [{ ...game, kickoff: "2026-09-11T14:00:00Z" }],
      venues,
      now,
    ).status,
    "unavailable",
  );
  assert.equal(
    weatherHealth(snapshot, [], venues, now + 30 * 3600000).status,
    "unavailable",
  );
  assert.equal(
    weatherHealth(snapshot, [], venues, now - 1).status,
    "unavailable",
  );
});
test("collection end cannot move a skipped game inside the eligibility window", () => {
  const later = now + 60000;
  const result = weatherHealth(
    { ...snapshot, generatedAt: new Date(later).toISOString(), games: {} },
    [{ ...game, kickoff: new Date(now + 7 * 86400000 + 30000).toISOString() }],
    venues,
    later,
  );
  assert.equal(result.status, "ok");
  assert.equal(result.eligibleGames, 0);
});
