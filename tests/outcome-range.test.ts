import { test } from "node:test";
import assert from "node:assert/strict";
import { marginRange } from "../src/lib/outcome-range";
test("margin endpoints name the correct side, including an even score", () => {
  assert.equal(marginRange([-14.1, 20.5], "Rams", "49ers"), "49ers by 14.1 to Rams by 20.5");
  assert.equal(marginRange([-12, -2], "Home", "Away"), "Away by 12.0 to Away by 2.0");
  assert.equal(marginRange([0, 5], "Home", "Away"), "an even score to Home by 5.0");
});
test("unusable intervals stay unavailable", () => {
  for (const interval of [[], [1], [2, 1], [NaN, 1], [-1, Infinity]])
    assert.equal(marginRange(interval, "Home", "Away"), null);
});
