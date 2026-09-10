import type { Game } from "./types";
export type PlayerReport = {
  season: number;
  type: string;
  week: number;
  team: string;
  playerId: string;
  name: string;
  position: string;
  reportStatus: string | null;
  practiceStatus: string | null;
  reportInjury: string | null;
  practiceInjury: string | null;
  practiceSecondaryInjury: string | null;
};
export type PersonnelSnapshot = {
  status: string;
  retrievedAt: string;
  assetUpdatedAt: string;
  sourceHash: string;
  players: PlayerReport[];
};
export function personnelForGame(
  snapshot: PersonnelSnapshot,
  game: Game,
  now = Date.now(),
) {
  const acquired = Date.parse(snapshot.retrievedAt),
    updated = Date.parse(snapshot.assetUpdatedAt),
    kickoff = Date.parse(game.kickoff ?? "");
  const expiresAt = Math.min(
    acquired + 30 * 3600000,
    updated + 30 * 3600000,
    kickoff,
  );
  const unavailable = (reason: string) => ({
    players: [] as PlayerReport[],
    reason,
    expiresAt: 0,
  });
  if (
    snapshot.status !== "available" ||
    ![acquired, updated, kickoff].every(Number.isFinite)
  )
    return unavailable("Personnel snapshot unavailable.");
  if (game.status === "final" || now >= kickoff || acquired >= kickoff)
    return unavailable("Pregame personnel context is closed for this game.");
  if (updated > acquired || acquired > now || updated > now || now >= expiresAt)
    return unavailable(
      "Personnel snapshot is outdated or awaiting a verified refresh.",
    );
  const type = ["WC", "DIV", "CON", "SB"].includes(game.type)
    ? "POST"
    : game.type;
  return {
    players: snapshot.players.filter(
      (r) =>
        r.season === game.season &&
        r.type === type &&
        r.week === game.week &&
        [game.home, game.away].includes(r.team),
    ),
    reason: null,
    expiresAt,
  };
}
