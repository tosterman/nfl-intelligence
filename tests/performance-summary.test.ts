import { test } from "node:test";
import assert from "node:assert/strict";
import { marginComparisonSummary } from "../src/lib/performance-summary";

test("margin conclusion follows the matched sample when relative performance reverses", () => {
  const metrics = { marketGames: 200, matchedModelMarginMae: 10, marketMarginMae: 9 };
  assert.match(marginComparisonSummary(metrics), /200 historical games.*closing market has the lower/);
  assert.match(marginComparisonSummary({ ...metrics, matchedModelMarginMae: 8 }), /the model has the lower/);
  assert.match(marginComparisonSummary({ ...metrics, matchedModelMarginMae: 9.001 }), /equal at the displayed precision/);
});

test("missing, invalid or empty matched evidence cannot generate a comparative claim", () => {
  const metrics = { marketGames: 200, matchedModelMarginMae: 10, marketMarginMae: 9 };
  for (const value of [null, NaN, Infinity, -1]) {
    assert.match(marginComparisonSummary({ ...metrics, matchedModelMarginMae: value }), /unavailable/);
    assert.match(marginComparisonSummary({ ...metrics, marketMarginMae: value }), /unavailable/);
  }
  for (const count of [0, -1, 0.5, NaN]) {
    assert.match(marginComparisonSummary({ ...metrics, marketGames: count }), /unavailable/);
  }
});
