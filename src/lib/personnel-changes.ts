import type { Game } from "./types";
import type { PersonnelSnapshot } from "./personnel";
export type PersonnelChange = {
  season: number;
  type: string;
  week: number;
  team: string;
  playerId: string;
  kind: string;
  playerName: string;
  position: string | null;
  observedAfter: string;
  observedBy: string;
  eventTime: null;
  fields: Record<string, { before: string | null; after: string | null }>;
};
export type PersonnelChanges = {
  schemaVersion: number;
  sourceHash: string;
  retrievedAt: string;
  previousRetrievedAt: string | null;
  changes: PersonnelChange[];
};
export function personnelChangesForGame(
  history: PersonnelChanges,
  snapshot: PersonnelSnapshot,
  game: Game,
) {
  const end = Date.parse(history.retrievedAt),
    start = Date.parse(history.previousRetrievedAt ?? "");
  if (
    history.schemaVersion !== 1 ||
    history.sourceHash !== snapshot.sourceHash ||
    history.retrievedAt !== snapshot.retrievedAt ||
    !Number.isFinite(end) ||
    !Number.isFinite(start) ||
    start >= end
  )
    return null;
  const type = ["WC", "DIV", "CON", "SB"].includes(game.type)
    ? "POST"
    : game.type;
  const changes = history.changes.filter(
    (c) =>
      c.season === game.season &&
      c.week === game.week &&
      c.type === type &&
      [game.home, game.away].includes(c.team),
  );
  if (
    changes.some(
      (c) =>
        c.observedAfter !== history.previousRetrievedAt ||
        c.observedBy !== history.retrievedAt ||
        c.eventTime !== null ||
        !["changed", "first-observed", "no-longer-present"].includes(c.kind),
    )
  )
    return null;
  return {
    start: history.previousRetrievedAt!,
    end: history.retrievedAt,
    changes,
  };
}
