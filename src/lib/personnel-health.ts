import type { PersonnelSnapshot } from "./personnel";
export function personnelHealth(
  snapshot: PersonnelSnapshot & { season: number },
  collection: { status: string; checkedAt: string },
  season: number,
  now = Date.now(),
) {
  const times = [
    snapshot.retrievedAt,
    snapshot.assetUpdatedAt,
    collection.checkedAt,
  ].map(Date.parse);
  const fresh = times.every(
    (t) => Number.isFinite(t) && t <= now && now - t < 30 * 3600000,
  );
  const valid =
    snapshot.status === "available" &&
    collection.status === "ok" &&
    Date.parse(snapshot.assetUpdatedAt) <= Date.parse(snapshot.retrievedAt) &&
    snapshot.season === season &&
    snapshot.players.length > 0 &&
    /^[a-f0-9]{64}$/.test(snapshot.sourceHash);
  return {
    status: fresh && valid ? "ok" : "unavailable",
    season: snapshot.season,
    expectedSeason: season,
    collectionStatus: collection.status,
    checkedAt: collection.checkedAt,
    retrievedAt: snapshot.retrievedAt,
    assetUpdatedAt: snapshot.assetUpdatedAt,
    sourceHash: snapshot.sourceHash,
    rowCount: snapshot.players.length,
    maximumAgeHours: 30,
    scope:
      "Collection and file freshness only; individual report dates and complete team coverage are not verified.",
  };
}
