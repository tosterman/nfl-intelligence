import { test } from "node:test";
import assert from "node:assert/strict";
import { quarterbackHealth } from "../src/lib/quarterback-health";
const at = "2026-09-10T12:00:00Z",
  now = Date.parse(at);
const snapshot = {
  season: 2026,
  retrievedAt: at,
  assetUpdatedAt: at,
  sourceHash: "a".repeat(64),
  sourceUrl: "https://example.com",
  teams: {
    A: {
      status: "available",
      recordedAt: at,
      listedFirst: "p",
      quarterbacks: [{ playerId: "p", rank: 1, name: "Player" }],
    },
  },
};
test("quarterback monitor rejects missing teams, failed collection, stale role and season mismatch", () => {
  const collection = { status: "ok", checkedAt: at };
  assert.equal(
    quarterbackHealth(
      { ...snapshot, retrievedAt: "2026-09-10T11:00:00Z" },
      collection,
      2026,
      ["A"],
      now,
    ).status,
    "unavailable",
  );
  assert.equal(
    quarterbackHealth(snapshot, collection, 2026, ["A"], now).status,
    "ok",
  );
  assert.equal(
    quarterbackHealth(snapshot, collection, 2026, ["A", "B"], now).status,
    "unavailable",
  );
  assert.equal(
    quarterbackHealth(
      snapshot,
      { ...collection, status: "unavailable" },
      2026,
      ["A"],
      now,
    ).status,
    "unavailable",
  );
  assert.equal(
    quarterbackHealth(snapshot, collection, 2025, ["A"], now).status,
    "unavailable",
  );
  assert.equal(
    quarterbackHealth(
      {
        ...snapshot,
        teams: {
          A: { ...snapshot.teams.A, recordedAt: "2026-09-08T12:00:00Z" },
        },
      },
      collection,
      2026,
      ["A"],
      now,
    ).status,
    "unavailable",
  );
});
