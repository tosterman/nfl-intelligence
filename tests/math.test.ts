import { test } from "node:test";
import assert from "node:assert/strict";
import {
  impliedProbability,
  fairMoneyline,
  noVig,
  compareMarket,
  gradeSpread,
  gradeTotal,
} from "../src/lib/math";

test("American odds round-trip, including even money", () => {
  for (const p of [0.1, 0.3, 0.5, 0.63, 0.9])
    assert.ok(Math.abs(impliedProbability(fairMoneyline(p)) - p) < 0.002);
  assert.equal(fairMoneyline(0.5), 100);
  assert.throws(() => impliedProbability(0));
  assert.throws(() => fairMoneyline(1));
});
test("two-sided market removes vig and sums to one", () => {
  const p = noVig(-110, -110);
  assert.equal(p.home, 0.5);
  assert.equal(p.away, 0.5);
});
test("home spread uses negative points for a favored home team", () => {
  const r = compareMarket(
    { homeMargin: 6, total: 49, homeWinProbability: 0.65 },
    {
      homeSpread: -3.5,
      total: 46.5,
      homeMoneyline: -145,
      awayMoneyline: 125,
      observedAt: "2026-09-10T10:00:00Z",
    },
    "2026-09-10T10:15:00Z",
  );
  assert.equal(r?.spreadDifference, 2.5);
  assert.equal(r?.totalDifference, 2.5);
});
test("missing, future and stale markets cannot produce an edge", () => {
  const p = { homeMargin: 6, total: 49, homeWinProbability: 0.65 };
  assert.equal(compareMarket(p, null, "2026-09-10T10:00:00Z"), null);
  for (const observedAt of [
    "2026-09-09T10:00:00Z",
    "2026-09-11T10:00:00Z",
    "bad",
  ])
    assert.equal(
      compareMarket(
        p,
        {
          homeSpread: -3.5,
          total: 46.5,
          homeMoneyline: -145,
          awayMoneyline: 125,
          observedAt,
        },
        "2026-09-10T10:00:00Z",
      ),
      null,
    );
});
test("pushes are graded explicitly", () => {
  assert.equal(gradeSpread(3, -3), "push");
  assert.equal(gradeSpread(4, -3), "win");
  assert.equal(gradeTotal(47, 47, "over"), "push");
  assert.equal(gradeTotal(46, 47, "under"), "win");
});

test("out-of-range model probability cannot produce market disagreement", () => {
  const market = {
    homeSpread: -3.5,
    total: 46.5,
    homeMoneyline: -145,
    awayMoneyline: 125,
    observedAt: "2026-09-10T10:00:00Z",
  };
  for (const homeWinProbability of [-0.1, 1.1]) {
    assert.equal(
      compareMarket(
        { homeMargin: 6, total: 49, homeWinProbability },
        market,
        "2026-09-10T10:15:00Z",
      ),
      null,
    );
  }
});
