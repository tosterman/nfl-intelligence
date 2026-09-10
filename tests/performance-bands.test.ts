import { test } from "node:test";
import assert from "node:assert/strict";
import site from "../data/site.json";
import {
  performanceBands,
  type DiagnosticRecord,
} from "../src/lib/performance-bands";
const record: DiagnosticRecord = {
  id: "g",
  season: 2024,
  week: 1,
  homeWinProbability: 0.6,
  homeMargin: 4,
  total: 44,
  actualMargin: 3,
  actualTotal: 40,
  marketMargin: 3,
};
test("retained confidence bands reconcile to the existing all-game record", () => {
  const groups = performanceBands(site.performance.records);
  const total = (key: "decisive" | "ties" | "correct") => groups.confidence.reduce((sum, band) => sum + band[key], 0);
  assert.equal(total("decisive"), site.performance.aggregate.decisiveGames);
  assert.equal(total("ties"), site.performance.aggregate.ties);
  assert.equal(total("correct"), site.performance.aggregate.wins);
  assert.equal(groups.confidence.flatMap(b => b.records).length, site.performance.aggregate.games);
  assert.equal(groups.disagreement.flatMap(b => b.records).length, site.performance.aggregate.marketGames);
});
test("fixed bands preserve boundary games, ties, missing markets and losses", () => {
  const rows = [
    record,
    {
      ...record,
      id: "tie",
      homeWinProbability: 0.5,
      actualMargin: 0,
      marketMargin: null,
    },
    {
      ...record,
      id: "miss",
      homeWinProbability: 0.8,
      homeMargin: -4,
      actualMargin: 5,
      marketMargin: 2,
    },
  ];
  const result = performanceBands(rows);
  assert.deepEqual(
    result.confidence.map((b) => b.records.length),
    [1, 1, 0, 1],
  );
  assert.equal(result.confidence[0].ties, 1);
  assert.equal(result.confidence[1].correct, 1);
  assert.equal(result.missingMarket, 1);
  assert.deepEqual(
    result.disagreement.map((b) => b.records.length),
    [1, 0, 0, 1],
  );
  assert.equal(result.disagreement[0].pushes, 1);
  assert.equal(result.disagreement[3].losses, 1);
  assert.equal(result.confidence[1].marginMae, 1);
  assert.equal(result.confidence[1].totalMae, 4);
});
test("invalid or duplicate records are rejected instead of silently changing samples", () => {
  for (const rows of [
    [record, record],
    [{ ...record, homeWinProbability: NaN }],
    [{ ...record, marketMargin: Infinity }],
  ]) {
    assert.throws(() => performanceBands(rows));
  }
  assert.equal(performanceBands([]).confidence[0].marginMae, null);
});
