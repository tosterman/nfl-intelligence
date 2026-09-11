export function participationHealth(
  source: {status: string; season: number; sourceHash: string; retrievedAt: string; rows: number},
  collection: {status: string; attemptedAt: string; sourceHash?: string; retrievedAt?: string; season: number},
  artifact: {sourceSeason: number; sourceHash: string; sourceRetrievedAt: string; calculatedAt: string; personnelSourceHash: string; personnelRetrievedAt: string},
  personnel: {sourceHash: string; retrievedAt: string}, season: number, now = Date.now(),
) {
  const acquired = Date.parse(source.retrievedAt), attempted = Date.parse(collection.attemptedAt), calculated = Date.parse(artifact.calculatedAt), reported = Date.parse(personnel.retrievedAt);
  const fresh = [acquired, attempted, calculated, reported].every(t => Number.isFinite(t) && t <= now && now - t < 30 * 3600000);
  const bound = source.status === 'available' && collection.status === 'collected' &&
    [source.season,collection.season,artifact.sourceSeason].every(s => s === season) &&
    /^[a-f0-9]{64}$/.test(source.sourceHash) && source.sourceHash === collection.sourceHash && source.sourceHash === artifact.sourceHash &&
    source.retrievedAt === collection.retrievedAt && source.retrievedAt === artifact.sourceRetrievedAt &&
    artifact.personnelSourceHash === personnel.sourceHash && artifact.personnelRetrievedAt === personnel.retrievedAt &&
    attempted <= acquired && acquired <= calculated && reported <= calculated && Number.isInteger(source.rows) && source.rows > 0;
  return {status: fresh && bound ? 'ok' : 'unavailable', season: source.season, expectedSeason: season,
    collectionStatus: collection.status, checkedAt: collection.attemptedAt, retrievedAt: source.retrievedAt,
    calculatedAt: artifact.calculatedAt, personnelRetrievedAt: personnel.retrievedAt,
    sourceHash: source.sourceHash, rowCount: source.rows, maximumAgeHours: 30,
    scope: 'Collection freshness and artifact binding only; not complete player coverage, current availability or nonempty weekly samples.'};
}
