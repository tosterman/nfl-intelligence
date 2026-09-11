import { test } from "node:test";
import assert from "node:assert/strict";
import evidence from "../data/source-record-changes.json";
import { scheduleSourceChanges } from "../src/lib/schedule-source-changes";

test("source explanations require the exact ordered hash pair and a compared game", () => {
  const game = evidence.comparedSiteGames[0];
  assert.ok(scheduleSourceChanges(game, evidence.beforeSha256, evidence.afterSha256));
  assert.equal(scheduleSourceChanges(game, evidence.afterSha256, evidence.beforeSha256), null);
  assert.equal(scheduleSourceChanges(game, undefined, evidence.afterSha256), null);
  assert.equal(scheduleSourceChanges("unknown", evidence.beforeSha256, evidence.afterSha256), null);
});

test("source explanation distinguishes this game's changes from other records", () => {
  const result = scheduleSourceChanges("2026_01_ATL_PIT", evidence.beforeSha256, evidence.afterSha256)!;
  assert.deepEqual(result.categories, ["Betting lines and prices"]);
  assert.equal(result.otherRecords, 18);
  const qb = scheduleSourceChanges("2026_02_SEA_ARI", evidence.beforeSha256, evidence.afterSha256)!;
  assert.ok(qb.categories.includes("Quarterback identity"));
});
