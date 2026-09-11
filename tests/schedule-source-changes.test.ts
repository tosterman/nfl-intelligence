import { test } from "node:test";
import assert from "node:assert/strict";
import evidence from "../data/source-record-changes.json";
import { scheduleSourceChanges } from "../src/lib/schedule-source-changes";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { RevisionHistory } from "../src/components/revision-history";
import type { Snapshot } from "../src/lib/types";

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

test("retained additional pairs remain separate from the historical comparison", () => {
  const pair = evidence.additionalPairs.find(pair => pair.beforeSha256 === pair.afterSha256)!;
  assert.ok(pair, 'Retained same-source comparison is required');
  const result = scheduleSourceChanges(pair.comparedSiteGames[0], pair.beforeSha256, pair.afterSha256);
  assert.deepEqual(result?.categories, []);
  assert.equal(result?.otherRecords, 0);
});

test("additional evidence renders without inventing legacy timestamp uncertainty or prediction deltas", () => {
  const pair = evidence.additionalPairs[0];
  const base = { gameId: pair.comparedSiteGames[0], generatedAt: "2026-09-10T10:00:00Z",
    modelVersion: "fixture", trainingThrough: "2026-09-09", trainingGames: 10,
    prediction: { homeWinProbability: 0.5, homeMargin: 0 } } as Snapshot;
  const html = renderToStaticMarkup(createElement(RevisionHistory, { history: [
    { ...base, hash: "before", sourceHash: pair.beforeSha256 },
    { ...base, hash: "after", generatedAt: "2026-09-11T10:00:00Z", sourceHash: pair.afterSha256 },
  ] }));
  assert.match(html, /Which schedule records changed/);
  assert.match(html, /File differences alone do not establish when information became public/);
  assert.doesNotMatch(html, /older file’s original collection time is unknown/);
  assert.match(html, /Not compared: original matchup context is missing or changed/);
});
