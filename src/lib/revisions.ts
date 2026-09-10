import type { Snapshot } from "./types";

export function sameRevisionContext(a: Snapshot, b: Snapshot) {
  const x = a.gameContext,
    y = b.gameContext;
  if (!x || !y || a.gameId !== b.gameId) return false;
  return (
    ["season", "week", "type", "home", "away", "venue", "neutral"].every(
      (key) =>
        x[key as keyof typeof x] != null &&
        x[key as keyof typeof x] === y[key as keyof typeof y],
    ) &&
    Number.isFinite(Date.parse(x.kickoff ?? "")) &&
    Date.parse(x.kickoff!) === Date.parse(y.kickoff ?? "")
  );
}

function stable(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
  if (value !== null && typeof value === "object")
    return `{${Object.entries(value)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${JSON.stringify(k)}:${stable(v)}`)
      .join(",")}}`;
  return JSON.stringify(value) ?? "undefined";
}

export function contributionChanges(previous: Snapshot, current: Snapshot) {
  if (
    !sameRevisionContext(previous, current) ||
    !previous.modelCodeHash ||
    previous.modelCodeHash !== current.modelCodeHash ||
    previous.modelVersion !== current.modelVersion ||
    !previous.configuration ||
    !current.configuration ||
    stable(previous.configuration) !== stable(current.configuration)
  )
    return null;
  const rounding = "Rounding reconciliation";
  const before = previous.prediction.contributions,
    after = current.prediction.contributions;
  for (const [terms, margin] of [
    [before, previous.prediction.homeMargin],
    [after, current.prediction.homeMargin],
  ] as const) {
    if (
      !Array.isArray(terms) ||
      !terms.length ||
      !Number.isFinite(margin) ||
      terms.some(
        (t) =>
          !t ||
          typeof t !== "object" ||
          typeof t.name !== "string" ||
          !t.name ||
          typeof t.detail !== "string" ||
          !t.detail ||
          !Number.isFinite(t.points),
      ) ||
      new Set(terms.map((t) => t.name)).size !== terms.length ||
      Math.abs(terms.reduce((sum, t) => sum + t.points, 0) - margin) > 1e-6
    )
      return null;
  }
  const a = new Map(before.map((t) => [t.name, t])),
    b = new Map(after.map((t) => [t.name, t]));
  const names = [...new Set([...a.keys(), ...b.keys()])];
  for (const name of names) {
    if (name !== rounding && (!a.has(name) || !b.has(name))) return null;
    if (
      a.has(name) &&
      b.has(name) &&
      a.get(name)!.detail !== b.get(name)!.detail
    )
      return null;
  }
  const rows = names.map((name) => ({
    name,
    before: a.get(name)?.points ?? 0,
    after: b.get(name)?.points ?? 0,
    change: (b.get(name)?.points ?? 0) - (a.get(name)?.points ?? 0),
  }));
  rows.sort((x, y) =>
    x.name === rounding
      ? 1
      : y.name === rounding
        ? -1
        : Math.abs(y.change) - Math.abs(x.change) ||
          x.name.localeCompare(y.name),
  );
  return {
    rows,
    marginChange:
      current.prediction.homeMargin - previous.prediction.homeMargin,
  };
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
