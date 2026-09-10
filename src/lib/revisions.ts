import type { Snapshot } from "./types";

function stable(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
  if (value !== null && typeof value === "object")
    return `{${Object.entries(value)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${JSON.stringify(k)}:${stable(v)}`)
      .join(",")}}`;
  return JSON.stringify(value) ?? "undefined";
}

export function compareRevisions(previous: Snapshot, current: Snapshot) {
  if (previous.gameId !== current.gameId)
    throw new Error("Cannot compare different games");
  const identities = [
    ["Model code changed", previous.modelCodeHash, current.modelCodeHash],
    [
      "Model configuration changed",
      previous.configuration,
      current.configuration,
    ],
    [
      "Schedule/results source changed",
      previous.sourceHash,
      current.sourceHash,
    ],
    [
      "Efficiency source changed",
      previous.efficiencySourceHashes,
      current.efficiencySourceHashes,
    ],
  ] as const;
  const changes: string[] = [];
  if (previous.modelVersion !== current.modelVersion)
    changes.push(
      `Model version changed: ${previous.modelVersion} → ${current.modelVersion}`,
    );
  for (const [label, before, after] of identities)
    if (
      before !== undefined &&
      after !== undefined &&
      stable(before) !== stable(after)
    )
      changes.push(label);
  if (
    previous.trainingThrough !== current.trainingThrough ||
    previous.trainingGames !== current.trainingGames
  )
    changes.push("Training sample changed");
  const completeProvenance = identities.every(
    ([, before, after]) => before !== undefined && after !== undefined,
  );
  const a = previous.prediction,
    b = current.prediction;
  return {
    changes,
    completeProvenance,
    homePoints: b.homeScore - a.homeScore,
    awayPoints: b.awayScore - a.awayScore,
    margin: b.homeMargin - a.homeMargin,
    total: b.total - a.total,
    probabilityPoints: 100 * (b.homeWinProbability - a.homeWinProbability),
  };
}
