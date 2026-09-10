import test from "node:test";
import assert from "node:assert/strict";
import type { PlayerReport } from "../src/lib/personnel";
import { usageForPlayer } from "../src/lib/player-usage";
const now = Date.parse("2026-09-11T00:00:00Z");
const player: PlayerReport = {
  playerId: "fixture",
  name: "Example Player",
  team: "PHI",
  season: 2026,
  type: "REG",
  week: 1,
  position: "LB",
  reportStatus: null,
  practiceStatus: null,
  reportInjury: null,
  practiceInjury: null,
  practiceSecondaryInjury: null,
};
const personnel = {
  sourceHash: "source",
  retrievedAt: "2026-09-10T10:00:00Z",
  assetUpdatedAt: "2026-09-10T09:00:00Z",
  status: "ok",
  players: [player],
};
const artifact = {
  schemaVersion: 1,
  personnelSourceHash: "source",
  personnelRetrievedAt: personnel.retrievedAt,
  sourceSeason: 2025,
  calculatedAt: "2026-09-10T11:00:00Z",
  records: [
    {
      ...player,
      identityStatus: "matched",
      usage: {
        status: "available",
        appearances: 8,
        lastAppearance: "2026-01-04T21:25:00Z",
        historicalTeams: ["PHI"],
        weightedShares: { offense_pct: 0, defense_pct: 0.5, st_pct: 0.1 },
      },
    },
  ],
};

test("verified usage exposes historical context without availability claims", () => {
  const value = usageForPlayer(artifact, personnel, player, now);
  assert.ok(value);
  assert.equal(value.season, 2025);
  assert.equal(value.appearances, 8);
  assert.ok(value.shares.defense_pct >= 0 && value.shares.defense_pct <= 1);
});
test("stale bindings, duplicate identity, invalid shares and dates are withheld", () => {
  for (const kind of [
    "binding",
    "duplicate",
    "conflicting-duplicate",
    "share",
    "date",
    "identity",
    "future",
  ]) {
    const copy = structuredClone(artifact);
    const row = copy.records.find((r) => r.playerId === player.playerId)!;
    if (kind === "binding") copy.personnelRetrievedAt = "2026-09-09T00:00:00Z";
    if (kind === "duplicate") copy.records.push(row);
    if (kind === "conflicting-duplicate")
      copy.records.push({ ...row, name: "Other" });
    if (kind === "share") row.usage.weightedShares!.defense_pct = 2;
    if (kind === "date") row.usage.lastAppearance = "invalid";
    if (kind === "identity") row.identityStatus = "identifier-mismatch";
    if (kind === "future") copy.calculatedAt = "2099-01-01T00:00:00Z";
    assert.equal(usageForPlayer(copy, personnel, player, now), null, kind);
  }
});
test("missing and name-conflicting reports never inherit another history", () => {
  assert.equal(
    usageForPlayer(artifact, personnel, { ...player, name: "Other" }, now),
    null,
  );
  const missing = { ...player, playerId: "missing" };
  assert.equal(usageForPlayer(artifact, personnel, missing, now), null);
});
