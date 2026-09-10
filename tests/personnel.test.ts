import { test } from "node:test";
import assert from "node:assert/strict";
import { personnelForGame } from "../src/lib/personnel";
import { personnelHealth } from "../src/lib/personnel-health";
import type { Game } from "../src/lib/types";
const game = {
  season: 2026,
  week: 1,
  type: "REG",
  home: "CAR",
  away: "CHI",
  kickoff: "2026-09-13T17:00:00Z",
  status: "scheduled",
} as Game;
const snapshot = {
  status: "available",
  retrievedAt: "2026-09-10T12:00:00Z",
  assetUpdatedAt: "2026-09-10T11:00:00Z",
  sourceHash: "a".repeat(64),
  players: [
    {
      season: 2026,
      week: 1,
      type: "REG",
      team: "CHI",
      playerId: "00-0030000",
      name: "Example Player",
      position: "QB",
      reportStatus: null,
      practiceStatus: "Limited Participation in Practice",
      reportInjury: null,
      practiceInjury: "Knee",
      practiceSecondaryInjury: null,
    },
  ],
};
const now = Date.parse(snapshot.retrievedAt);
test("source updates after acquisition are withheld even when both dates are fresh", () => {
  const data = {
    ...snapshot,
    season: 2026,
    retrievedAt: new Date(now - 2 * 3600000).toISOString(),
  };
  assert.equal(
    personnelHealth(
      data,
      { status: "ok", checkedAt: data.retrievedAt },
      2026,
      now,
    ).status,
    "unavailable",
  );
  assert.equal(personnelForGame(data, game, now).players.length, 0);
});
test("personnel health distinguishes failed collection and stale sources from fresh downloads", () => {
  const data = { ...snapshot, season: 2026 };
  const collection = { status: "ok", checkedAt: snapshot.retrievedAt };
  assert.equal(personnelHealth(data, collection, 2026, now).status, "ok");
  assert.equal(
    personnelHealth(data, { ...collection, status: "unavailable" }, 2026, now)
      .status,
    "unavailable",
  );
  assert.equal(
    personnelHealth(data, collection, 2027, now).status,
    "unavailable",
  );
  assert.equal(
    personnelHealth(
      { ...data, assetUpdatedAt: new Date(now - 30 * 3600000).toISOString() },
      collection,
      2026,
      now,
    ).status,
    "unavailable",
  );
  assert.equal(
    personnelHealth({ ...data, sourceHash: "bad" }, collection, 2026, now)
      .status,
    "unavailable",
  );
});
test("personnel matches only exact scope and preserves blank designations", () => {
  const result = personnelForGame(snapshot, game, now);
  assert.ok(result.players.length > 0);
  assert.ok(
    result.players.every(
      (p) => [game.home, game.away].includes(p.team) && p.week === game.week,
    ),
  );
  assert.ok(result.players.some((p) => p.reportStatus === null));
  assert.equal(
    personnelForGame(snapshot, { ...game, week: 2 }, now).players.length,
    0,
  );
  assert.equal(
    personnelForGame(snapshot, { ...game, type: "POST" }, now).players.length,
    0,
  );
});
test("postseason phases map without matching regular season reports", () => {
  const data = {
    ...snapshot,
    players: snapshot.players.map((p) => ({ ...p, type: "POST", week: 19 })),
  };
  assert.ok(
    personnelForGame(data, { ...game, type: "WC", week: 19 }, now).players
      .length > 0,
  );
  assert.equal(
    personnelForGame(data, { ...game, week: 19 }, now).players.length,
    0,
  );
});
test("fresh downloads cannot revive old assets; kickoff and future dates withhold rows", () => {
  for (const data of [
    { ...snapshot, assetUpdatedAt: new Date(now - 31 * 3600000).toISOString() },
    { ...snapshot, retrievedAt: new Date(now + 1000).toISOString() },
    { ...snapshot, assetUpdatedAt: "bad" },
  ])
    assert.equal(personnelForGame(data, game, now).players.length, 0);
  assert.equal(
    personnelForGame(snapshot, game, Date.parse(game.kickoff!)).players.length,
    0,
  );
  assert.equal(
    personnelForGame(snapshot, { ...game, status: "final" }, now).players
      .length,
    0,
  );
});
