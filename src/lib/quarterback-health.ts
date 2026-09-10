import type { QuarterbackSnapshot } from "./quarterbacks";
export function quarterbackHealth(
  snapshot: QuarterbackSnapshot,
  collection: { status: string; checkedAt: string },
  season: number,
  teams: string[],
  now = Date.now(),
) {
  const fresh = (value: string | null | undefined) => {
    const at = Date.parse(value ?? "");
    return Number.isFinite(at) && at <= now && now - at < 30 * 3600000;
  };
  const expected = [...new Set(teams)].sort();
  const checks = expected.map((team) => {
    const role = snapshot.teams[team];
    const leaders = role?.quarterbacks.filter((p) => p.rank === 1) ?? [];
    const valid =
      role?.status === "available" &&
      fresh(role.recordedAt) &&
      Date.parse(role.recordedAt ?? "") <= Date.parse(snapshot.retrievedAt) &&
      leaders.length > 0 &&
      leaders.every(
        (p) => p.playerId === role.listedFirst && p.name === leaders[0].name,
      );
    return {
      team,
      status: valid ? "ok" : "unavailable",
      recordedAt: role?.recordedAt ?? null,
    };
  });
  const valid =
    collection.status === "ok" &&
    snapshot.season === season &&
    Date.parse(snapshot.assetUpdatedAt) <= Date.parse(snapshot.retrievedAt) &&
    /^[a-f0-9]{64}$/.test(snapshot.sourceHash) &&
    [snapshot.retrievedAt, snapshot.assetUpdatedAt, collection.checkedAt].every(
      fresh,
    ) &&
    checks.length > 0 &&
    checks.every((c) => c.status === "ok");
  return {
    status: valid ? "ok" : "unavailable",
    season: snapshot.season,
    expectedSeason: season,
    collectionStatus: collection.status,
    checkedAt: collection.checkedAt,
    retrievedAt: snapshot.retrievedAt,
    assetUpdatedAt: snapshot.assetUpdatedAt,
    sourceHash: snapshot.sourceHash,
    maximumAgeHours: 30,
    expectedTeams: expected,
    checks,
    scope:
      "Recent listed quarterback roles, not confirmed starters or verified announcement times.",
  };
}
