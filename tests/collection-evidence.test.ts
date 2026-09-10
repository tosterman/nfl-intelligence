import { test } from "node:test";
import assert from "node:assert/strict";
import { collectionResult } from "../src/lib/collection-evidence";
const now = Date.parse("2026-09-10T20:00:00Z");
const captured = {
  status: "captured",
  fetchedAt: new Date(now).toISOString(),
  sha256: "a".repeat(64),
  events: 239,
  creditsRemaining: "470",
};
test("collection evidence retains only known fields and distinguishes reuse", () => {
  assert.deepEqual(
    collectionResult(
      { ...captured, apiKey: "do-not-log", rawResponse: "private" },
      now,
    ),
    captured,
  );
  assert.deepEqual(
    collectionResult({ ...captured, status: "already-current" }, now),
    { status: "already-current", fetchedAt: captured.fetchedAt },
  );
  assert.equal(
    collectionResult({ ...captured, creditsRemaining: null }, now)
      .creditsRemaining,
    null,
  );
});
test("unproven capture, invalid quota, and stale or future acquisition are rejected", () => {
  for (const change of [
    { status: "ok" },
    { sha256: "" },
    { events: -1 },
    { events: 1.5 },
    { creditsRemaining: "unknown" },
    { creditsRemaining: undefined },
    { fetchedAt: "bad" },
    { fetchedAt: new Date(now + 1).toISOString() },
    { fetchedAt: new Date(now - 120001).toISOString() },
  ])
    assert.throws(() => collectionResult({ ...captured, ...change }, now));
  assert.throws(() =>
    collectionResult(
      {
        ...captured,
        status: "already-current",
        fetchedAt: new Date(now - 1920001).toISOString(),
      },
      now,
    ),
  );
});

test("reuse evidence allows bounded response transit beyond the server reuse cutoff", () => {
  assert.equal(
    collectionResult(
      {
        ...captured,
        status: "already-current",
        fetchedAt: new Date(now - 1801000).toISOString(),
      },
      now,
    ).status,
    "already-current",
  );
});
