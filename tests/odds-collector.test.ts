import { test } from "node:test";
import assert from "node:assert/strict";
import { authorizedCollector } from "../src/lib/odds-collector";
test("collection requires a configured long secret and exact bearer credential", () => {
  const secret = "a".repeat(64);
  assert.equal(authorizedCollector(null, secret), false);
  assert.equal(authorizedCollector("Bearer " + secret, undefined), false);
  assert.equal(authorizedCollector("Bearer " + secret, secret), true);
  assert.equal(authorizedCollector("Bearer " + secret + "x", secret), false);
  assert.equal(authorizedCollector("Bearer weak", "weak"), false);
});
