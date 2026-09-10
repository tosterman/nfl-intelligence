import { test } from "node:test";
import assert from "node:assert/strict";
import { weatherStatus, type WeatherRecord } from "../src/lib/weather";
const game = { venue: "Venue", kickoff: "2026-09-13T17:00:00Z" };
const record: WeatherRecord = {
  ...game,
  status: "available",
  issuedAt: "2026-09-10T10:00:00Z",
  retrievedAt: "2026-09-10T12:00:00Z",
  periodStart: "2026-09-13T17:00:00Z",
  periodEnd: "2026-09-13T18:00:00Z",
};
const now = Date.parse("2026-09-10T13:00:00Z");
test("fresh matching weather may be shown", () =>
  assert.equal(weatherStatus(record, game, now), "available"));
test("rescheduled games cannot reuse prior venue or kickoff forecast", () => {
  assert.notEqual(
    weatherStatus(record, { ...game, venue: "Elsewhere" }, now),
    "available",
  );
  assert.notEqual(
    weatherStatus(record, { ...game, kickoff: "2026-09-13T18:00:00Z" }, now),
    "available",
  );
});
test("missing and old issue time cannot be made fresh by acquisition", () => {
  assert.notEqual(
    weatherStatus({ ...record, issuedAt: undefined }, game, now),
    "available",
  );
  assert.notEqual(
    weatherStatus({ ...record, issuedAt: "2026-09-08T12:00:00Z" }, game, now),
    "available",
  );
});
test("period must contain kickoff", () =>
  assert.notEqual(
    weatherStatus({ ...record, periodEnd: game.kickoff! }, game, now),
    "available",
  ));
