import type { Game } from "./types";

export function nextScheduledGame(games: Game[], team: string): Game | undefined {
  return games
    .filter((game) => (game.home === team || game.away === team) && game.status === "scheduled")
    .sort((a, b) => a.season - b.season || a.week - b.week ||
      (a.kickoff ?? "z").localeCompare(b.kickoff ?? "z") || a.id.localeCompare(b.id))[0];
}
