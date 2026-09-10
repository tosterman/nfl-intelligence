import { test } from "node:test";
import assert from "node:assert/strict";
import { orderRatings } from "../src/lib/ratings-order";
test("ratings order changes the selected metric without mutating model output", () => {
  const rows = [{ team: "B", rating: 2, offense: 1, defense: 4 }, { team: "A", rating: 3, offense: 1, defense: -1 }];
  const original = structuredClone(rows);
  assert.deepEqual(orderRatings(rows, "defense").map(r => r.team), ["B", "A"]);
  assert.deepEqual(orderRatings(rows, "offense").map(r => r.team), ["A", "B"]);
  assert.deepEqual(orderRatings(rows, "unexpected").map(r => r.team), ["A", "B"]);
  assert.deepEqual(rows, original);
});
