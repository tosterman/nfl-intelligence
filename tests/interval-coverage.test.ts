import { test } from "node:test";
import assert from "node:assert/strict";
import { intervalCoverage } from "../src/lib/interval-coverage";
import { site } from "../src/lib/data";

test("coverage includes endpoints, reports widths and excludes missing markets only from bands", () => {
  const base = {
    ...site.performance.records[0],
    marginInterval80: [-10, 10],
    totalInterval80: [30, 60],
    actualMargin: -10,
    actualTotal: 70,
    homeMargin: 7,
    marketMargin: 1,
  };
  const rows = intervalCoverage([
    base,
    {
      ...base,
      id: "second",
      marketMargin: null,
      actualMargin: 11,
      actualTotal: 60,
    },
  ]);
  assert.equal(rows.all.margin.covered, 1);
  assert.equal(rows.all.total.covered, 1);
  assert.equal(rows.all.margin.meanWidth, 20);
  assert.equal(rows.all.total.meanWidth, 30);
  assert.equal(rows.disagreement[3].games, 1);
  assert.equal(rows.disagreement[3].margin.covered, 1);
  assert.equal(rows.missingMarket, 1);
  assert.equal(rows.disagreement[0].margin.meanWidth, null);
  assert.throws(() =>
    intervalCoverage([{ ...base, marginInterval80: [10, -10] }]),
  );
  assert.throws(() =>
    intervalCoverage([{ ...base, totalInterval80: [0, NaN] }]),
  );
  assert.throws(() => intervalCoverage([base, base]));
});

test("current edition reconciles with the independently computed Python audit", () => {
  const rows = intervalCoverage(site.performance.records);
  assert.equal(rows.all.games, 570);
  assert.equal(rows.all.margin.covered, 463);
  assert.equal(rows.all.total.covered, 470);
  assert.equal(rows.disagreement[3].games, 35);
  assert.equal(rows.disagreement[3].margin.covered, 22);
  assert.equal(
    rows.disagreement.reduce((n, r) => n + r.games, rows.missingMarket),
    rows.all.games,
  );
});
