import type { Game } from "./types";

export function scheduleSpacing(game: Game, games: Game[], now = Date.now()) {
  const kickoff = Date.parse(game.kickoff ?? "");
  return [game.away, game.home].map((team) => {
    const unknown = (reason: string) => ({
      team,
      previous: null,
      days: null,
      reason,
    });
    if (!Number.isFinite(kickoff) || !Number.isFinite(now))
      return unknown("Kickoff timing is unverified.");
    const candidates = games.filter(
      (g) =>
        g.id !== game.id &&
        g.season === game.season &&
        [g.home, g.away].includes(team),
    );
    if (
      candidates.some(
        (g) =>
          g.week < game.week && !Number.isFinite(Date.parse(g.kickoff ?? "")),
      )
    )
      return unknown("An earlier game has unverified kickoff timing.");
    const prior = candidates
      .filter((g) => Date.parse(g.kickoff ?? "") < kickoff)
      .sort((a, b) => Date.parse(b.kickoff!) - Date.parse(a.kickoff!));
    if (!prior.length)
      return unknown("No earlier same-season game is recorded.");
    const previous = prior[0];
    if (
      prior.filter(
        (g) =>
          Date.parse(g.kickoff!) === Date.parse(previous.kickoff!) ||
          g.id === previous.id,
      ).length !== 1
    )
      return unknown("Previous-game identity is ambiguous.");
    if (
      previous.status !== "final" ||
      !Number.isFinite(previous.actualHome) ||
      !Number.isFinite(previous.actualAway) ||
      previous.actualHome === null ||
      previous.actualAway === null
    )
      return unknown(
        "The preceding scheduled game has no verified final result yet.",
      );
    if (Date.parse(previous.kickoff!) + 86400000 >= Math.min(now, kickoff))
      return unknown(
        "The previous game is within the 24-hour verification window.",
      );
    return {
      team,
      previous,
      days: (kickoff - Date.parse(previous.kickoff!)) / 86400000,
      reason: null,
    };
  });
}
