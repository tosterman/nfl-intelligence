import { test } from "node:test";
import assert from "node:assert/strict";
import {
  authorizedCollector,
  canReuseSnapshot,
} from "../src/lib/odds-collector";
test("collection requires a configured long secret and exact bearer credential", () => {
  const secret = "a".repeat(64);
  assert.equal(authorizedCollector(null, secret), false);
  assert.equal(authorizedCollector("Bearer " + secret, undefined), false);
  assert.equal(authorizedCollector("Bearer " + secret, secret), true);
  assert.equal(authorizedCollector("Bearer " + secret + "x", secret), false);
  assert.equal(authorizedCollector("Bearer weak", "weak"), false);
});
test("manual collection cannot suppress a scheduled capture for hours", () => {
  const feed = {
    state: "ready" as const,
    fetchedAt: "2026-09-10T14:17:00Z",
    events: [],
  };
  const fetched = Date.parse(feed.fetchedAt);
  assert.equal(canReuseSnapshot(feed, fetched + 29 * 60000), true);
  assert.equal(canReuseSnapshot(feed, fetched + 30 * 60000), false);
  assert.equal(canReuseSnapshot(feed, fetched + 2 * 3600000), false);
});
