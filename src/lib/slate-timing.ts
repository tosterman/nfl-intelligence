import type { Game } from "./types";

export function featuredGame(games: Game[], now: number) {
  return games.filter(game => game.snapshot && game.status === "scheduled" &&
    Number.isFinite(now) && Date.parse(game.kickoff ?? "") > now)
    .sort((a, b) => Date.parse(a.kickoff!) - Date.parse(b.kickoff!))[0];
}

export function slateGameStatus(game: Game, now: number) {
  if (game.status === "final") return "Final";
  const kickoff = Date.parse(game.kickoff ?? "");
  if (Number.isFinite(kickoff) && kickoff <= now) return "Awaiting verified result";
  return game.snapshot ? "Model forecast" : "Awaiting forecast";
}
