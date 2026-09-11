import { compareRevisions, contributionChanges, sameRevisionContext } from "./revisions";
import { snapshotTime, type Game, type Snapshot } from "./types";

export type WeeklyChange = {
  game: Game;
  current: Snapshot;
  previous?: Snapshot;
  kind: "first" | "revision" | "model" | "unavailable";
  note: string;
  delta?: ReturnType<typeof compareRevisions>;
  contribution?: { name: string; change: number };
};

export function weeklyBriefing(games: Game[], asOf: number) {
  const changes = weeklyChanges(games, asOf);
  return {
    changes: changes.map(({ game, current, previous, ...rest }) => ({
      ...rest,
      game: { id: game.id, away: game.away, home: game.home, neutral: game.neutral },
      current: { generatedAt: snapshotTime(current) },
      previous: previous ? { generatedAt: snapshotTime(previous) } : undefined,
    })),
    unavailableIds: games.filter(game => changes.some(row => row.game.id === game.id && row.kind === "unavailable") || (!game.snapshot && game.history.length > 0)).map(game => game.id),
  };
}
export type WeeklyBriefing = ReturnType<typeof weeklyBriefing>;

function validPrediction(s: Snapshot) {
  const p = s.prediction;
  return p && [p.homeScore, p.awayScore, p.homeMargin, p.total, p.homeWinProbability].every(Number.isFinite)
    && p.homeWinProbability >= 0 && p.homeWinProbability <= 1;
}
function completeIdentity(s: Snapshot) {
  return [s.modelVersion, s.modelCodeHash, s.sourceHash].every((value) => typeof value === "string" && value.length > 0)
    && s.configuration != null && typeof s.configuration === "object" && !Array.isArray(s.configuration)
    && Array.isArray(s.efficiencySourceHashes) && s.efficiencySourceHashes.length > 0
    && s.efficiencySourceHashes.every((value) => typeof value === "string" && value.length > 0);
}

export function weeklyChanges(games: Game[], asOf: number): WeeklyChange[] {
  const result: WeeklyChange[] = [];
  for (const game of games) {
    const current = game.snapshot;
    if (!current) continue;
    const currentTime = Date.parse(snapshotTime(current));
    const entry: WeeklyChange = { game, current, kind: "unavailable", note: "Comparable revision history unavailable." };
    const matches = game.history.filter((s) => s.hash === current.hash);
    const index = game.history.findIndex((s) => s.hash === current.hash);
    if (!Number.isFinite(asOf) || !Number.isFinite(currentTime) || currentTime > asOf ||
        !validPrediction(current) || matches.length !== 1 ||
        !sameRevisionContext(current, { ...current, gameId: game.id, gameContext: game })) {
      result.push(entry); continue;
    }
    if (index === 0) {
      result.push({ ...entry, kind: "first", note: "First retained forecast for this matchup." }); continue;
    }
    const previous = game.history[index - 1];
    const previousTime = Date.parse(snapshotTime(previous));
    entry.previous = previous;
    if (!Number.isFinite(previousTime) || previousTime >= currentTime || !validPrediction(previous)) {
      result.push({ ...entry, note: "The previous run has an invalid time or prediction; changes cannot be compared." }); continue;
    }
    if (!previous.gameContext) {
      result.push({ ...entry, note: "The previous run did not retain its original matchup details, so a reliable comparison is unavailable." }); continue;
    }
    if (!sameRevisionContext(previous, current)) {
      result.push({ ...entry, note: "The recorded matchup details changed between runs; inspect them separately." }); continue;
    }
    const delta = compareRevisions(previous, current);
    if (!delta.completeProvenance || !completeIdentity(previous) || !completeIdentity(current)) {
      result.push({ ...entry, note: "Prior model or source identity is incomplete." }); continue;
    }
    if (delta.changes.some((change) => change.startsWith("Model "))) {
      result.push({ ...entry, kind: "model", note: "Model definition changed; inspect the revision separately." }); continue;
    }
    const leading = contributionChanges(previous, current)?.rows.find((row) => row.name !== "Rounding reconciliation" && Number(Math.abs(row.change).toFixed(3)) >= 0.001);
    result.push({ ...entry, kind: "revision", delta,
      note: delta.margin === 0 && delta.probabilityPoints === 0 && delta.total === 0
        ? "Latest revision leaves margin, total and win chance unchanged."
        : "Latest forecast compared with its immediate predecessor.",
      contribution: leading ? { name: leading.name, change: leading.change } : undefined });
  }
  return result.sort((a, b) => {
    const priority = { revision: 0, model: 1, first: 2, unavailable: 3 };
    return priority[a.kind] - priority[b.kind] ||
      Math.abs(b.delta?.margin ?? 0) - Math.abs(a.delta?.margin ?? 0) ||
      Math.abs(b.delta?.probabilityPoints ?? 0) - Math.abs(a.delta?.probabilityPoints ?? 0) ||
      a.game.id.localeCompare(b.game.id);
  });
}
