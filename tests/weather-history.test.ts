import { test } from "node:test";
import assert from "node:assert/strict";
import { weatherHistoryForGame, type WeatherObservation } from "../src/lib/weather-history";
const game = { id: "game", venue: "Venue", kickoff: "2026-09-13T17:00:00Z" };
const first: WeatherObservation = { ...game, gameId: game.id, status: "available", issuedAt: "2026-09-10T12:00:00Z",
  retrievedAt: "2026-09-10T13:00:00Z", temperature: 70, temperatureUnit: "F", windSpeed: "5 to 10 mph",
  sourceHash: "source1", hash: "first", locationHash: "location" };
const current = { ...first, issuedAt: "2026-09-11T12:00:00Z", retrievedAt: "2026-09-11T13:00:00Z", temperature: 73, sourceHash: "source2", hash: "current" };
const select = (records: WeatherObservation[], anchor: WeatherObservation = current) => weatherHistoryForGame({ schemaVersion: 1, records }, anchor, game);
test("retained issues collapse repeat captures and preserve raw wind ranges", () => {
  const repeat = { ...first, retrievedAt: "2026-09-10T14:00:00Z", hash: "repeat" };
  const result = select([current, repeat, first])!;
  assert.equal(result.issues.length, 2);
  assert.equal(result.issues[1].hash, "repeat");
  assert.equal(result.issues[1].windSpeed, "5 to 10 mph");
  assert.equal(result.changed, true);
});
test("different kickoff, venue and location cannot enter comparison", () => {
  const rows = [{ ...first, kickoff: "2026-09-13T18:00:00Z" }, { ...first, venue: "Other" }, { ...first, locationHash: "other" }, current];
  assert.equal(select(rows)!.issues.length, 1);
  assert.equal(select([first]), null);
});
test("unchanged values, missing fields and contradictory issue values stay explicit", () => {
  const unchanged = { ...current, temperature: 70 };
  assert.equal(select([first, unchanged], unchanged)!.changed, false);
  const missing = { ...current, temperature: null };
  assert.equal(select([first, missing], missing)!.issues[0].temperature, null);
  const conflict = { ...first, temperature: 72, hash: "conflict" };
  assert.equal(select([first, conflict, current]), null);
});
test("later captured observations cannot leak into earlier current record", () => {
  const future = { ...first, retrievedAt: "2026-09-12T13:00:00Z", hash: "future" };
  assert.equal(select([future, current])!.issues.length, 1);
});
