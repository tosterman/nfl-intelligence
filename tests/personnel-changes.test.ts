import { test } from "node:test";
import assert from "node:assert/strict";
import {
  personnelChangesForGame,
  type PersonnelChanges,
} from "../src/lib/personnel-changes";
import type { Game } from "../src/lib/types";
const game = {
  season: 2026,
  week: 1,
  type: "REG",
  home: "CAR",
  away: "CHI",
} as Game;
const snapshot = {
  status: "available",
  retrievedAt: "2026-09-10T12:00:00Z",
  assetUpdatedAt: "2026-09-10T11:00:00Z",
  sourceHash: "a".repeat(64),
  players: [],
};
const change = {
  season: 2026,
  week: 1,
  type: "REG",
  team: "CHI",
  playerId: "id",
  playerName: "Example",
  position: "QB",
  kind: "changed",
  observedAfter: "2026-09-10T10:00:00Z",
  observedBy: snapshot.retrievedAt,
  eventTime: null,
  fields: { reportStatus: { before: "Questionable", after: "Out" } },
};
const history: PersonnelChanges = {
  schemaVersion: 1,
  sourceHash: snapshot.sourceHash,
  retrievedAt: snapshot.retrievedAt,
  previousRetrievedAt: change.observedAfter,
  changes: [change],
};
test("personnel changes are scoped to exact teams, season, week and competition", () => {
  assert.equal(
    personnelChangesForGame(history, snapshot, game)?.changes.length,
    1,
  );
  for (const patch of [
    { season: 2025 },
    { week: 2 },
    { type: "PRE" },
    { team: "DAL" },
  ])
    assert.equal(
      personnelChangesForGame(
        { ...history, changes: [{ ...change, ...patch }] },
        snapshot,
        game,
      )?.changes.length,
      0,
    );
});
test("mismatched snapshot, unknown interval and invalid chronology cannot imply no changes", () => {
  for (const patch of [
    { sourceHash: "b".repeat(64) },
    { retrievedAt: "2026-09-10T13:00:00Z" },
    { previousRetrievedAt: null },
    { previousRetrievedAt: snapshot.retrievedAt },
  ])
    assert.equal(
      personnelChangesForGame({ ...history, ...patch }, snapshot, game),
      null,
    );
  assert.equal(
    personnelChangesForGame(
      {
        ...history,
        changes: [{ ...change, observedBy: "2026-09-11T12:00:00Z" }],
      },
      snapshot,
      game,
    ),
    null,
  );
});
test("missing rows retain their distinct status and postseason uses source competition type", () => {
  const h = {
    ...history,
    changes: [{ ...change, kind: "no-longer-present", type: "POST" }],
  };
  assert.equal(
    personnelChangesForGame(h, snapshot, { ...game, type: "WC" })?.changes[0]
      .kind,
    "no-longer-present",
  );
});
