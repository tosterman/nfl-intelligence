import { test } from "node:test";
import assert from "node:assert/strict";
import { compareRevisions, sameRevisionContext } from "../src/lib/revisions";
import type { Snapshot } from "../src/lib/types";

const original: Snapshot = {
  gameId: "g",
  modelVersion: "v1",
  hash: "a",
  trainingGames: 400,
  trainingThrough: "2026-09-01",
  sourceHash: "source",
  modelCodeHash: "code",
  efficiencySourceHashes: ["epa"],
  configuration: { ridge: 6, weight: 0.25 },
  prediction: {
    homeScore: 24,
    awayScore: 21,
    homeMargin: 3,
    total: 45,
    homeWinProbability: 0.6,
    marginInterval80: [-10, 16],
    totalInterval80: [30, 60],
    sigmaMargin: 14,
    sigmaTotal: 14,
    contributions: [],
  },
};
test("source refresh does not imply a football adjustment", () => {
  const diff = compareRevisions(original, {
    ...original,
    sourceHash: "revised",
  });
  assert.deepEqual(diff.changes, ["Schedule/results source changed"]);
  assert.equal(diff.margin, 0);
  assert.equal(diff.probabilityPoints, 0);
});
test("code changes are detected even when version label stays constant", () => {
  assert.deepEqual(
    compareRevisions(original, { ...original, modelCodeHash: "fixed" }).changes,
    ["Model code changed"],
  );
});
test("configuration key order is immaterial and reruns are not called source changes", () => {
  assert.deepEqual(
    compareRevisions(original, {
      ...original,
      hash: "new",
      generatedAt: "2026-09-02",
      configuration: { weight: 0.25, ridge: 6 },
    }).changes,
    [],
  );
});
test("missing legacy provenance is not a claim of unchanged inputs", () => {
  const legacy = {
    ...original,
    sourceHash: undefined,
    modelCodeHash: undefined,
  };
  assert.equal(compareRevisions(legacy, original).completeProvenance, false);
});
test("revision deltas preserve direction and percentage-point units", () => {
  const diff = compareRevisions(original, {
    ...original,
    prediction: {
      ...original.prediction,
      homeScore: 22,
      awayScore: 23,
      homeMargin: -1,
      total: 45,
      homeWinProbability: 0.45,
    },
  });
  assert.equal(diff.homePoints, -2);
  assert.equal(diff.awayPoints, 2);
  assert.equal(diff.margin, -4);
  assert.equal(diff.total, 0);
  assert.ok(Math.abs(diff.probabilityPoints + 15) < 1e-10);
});
test("revision comparison refuses unrelated games", () => {
  assert.throws(() =>
    compareRevisions(original, { ...original, gameId: "other" }),
  );
});

test("revision comparisons require matching recorded matchup context", () => {
  const gameContext = {
    season: 2026,
    week: 1,
    type: "REG",
    home: "PHI",
    away: "DAL",
    kickoff: "2026-09-10T20:00:00Z",
    venue: "Example",
    neutral: false,
  };
  const snap = { ...original, gameContext };
  assert.equal(sameRevisionContext(original, original), false);
  assert.equal(
    sameRevisionContext(snap, {
      ...snap,
      gameContext: { ...gameContext, kickoff: "2026-09-10T16:00:00-04:00" },
    }),
    true,
  );
  for (const change of [
    { kickoff: "2026-09-11T20:00:00Z" },
    { venue: "Other" },
    { neutral: true },
    { home: "DAL" },
    { week: 2 },
  ])
    assert.equal(
      sameRevisionContext(snap, {
        ...snap,
        gameContext: { ...gameContext, ...change },
      }),
      false,
    );
});
