import type { Snapshot } from './types';
export type TotalTerm = {name: string; points: number};
export type TotalExplanation = {snapshotHash: string; gameId: string; total: number; terms: TotalTerm[]};
export type TotalEvidence = {schemaVersion: number; modelCodeHash: string; inputManifestSha256: string;
  explanationCodeHash: string; records: Record<string, TotalExplanation>;
  retainedRecords?: Record<string, {schemaVersion: number; modelCodeHash: string;
    explanationCodeHash: string; inputManifestSha256: string; artifactSha256: string; record: TotalExplanation}>};

export function selectTotalExplanation(evidence: TotalEvidence, snapshot: Snapshot): (TotalExplanation & {baseline: number; adjustment: number}) | null {
  if (!Object.hasOwn(evidence.records, snapshot.hash) && evidence.retainedRecords &&
      Object.hasOwn(evidence.retainedRecords, snapshot.hash)) {
    const origin = evidence.retainedRecords[snapshot.hash];
    if (!/^[a-f0-9]{64}$/.test(origin.artifactSha256)) return null;
    return selectTotalExplanation({...origin, records: {[snapshot.hash]: origin.record}}, snapshot);
  }
  if (evidence.schemaVersion !== 1 || evidence.modelCodeHash !== snapshot.modelCodeHash ||
      ![evidence.inputManifestSha256, evidence.explanationCodeHash, snapshot.hash].every(v => /^[a-f0-9]{64}$/.test(v)) ||
      !Object.hasOwn(evidence.records, snapshot.hash)) return null;
  const row = evidence.records[snapshot.hash];
  if (row.snapshotHash !== snapshot.hash || row.gameId !== snapshot.gameId || row.total !== snapshot.prediction.total ||
      !Number.isFinite(row.total) || !row.terms.length || row.terms.some(t => !t.name || !Number.isFinite(t.points)) ||
      new Set(row.terms.map(t => t.name)).size !== row.terms.length ||
      Math.abs(row.terms.reduce((sum, t) => sum + t.points, 0) - row.total) > 1e-7) return null;
  const baselines = row.terms.filter(t => t.name === 'Scoring baseline' || t.name === 'Efficiency intercept');
  if (baselines.length !== 2) return null;
  const baseline = baselines.reduce((sum, t) => sum + t.points, 0);
  return {...row, baseline, adjustment: row.total - baseline};
}
