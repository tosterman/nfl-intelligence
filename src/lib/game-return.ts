import { teams } from "./teams";

export function gameReturn(from: unknown, game: { home: string; away: string; week: number }) {
  if (typeof from === "string") {
    const team = [game.home, game.away].find(code => from === `/teams/${code.toLowerCase()}` && teams[code]);
    if (team) return { href: `/teams/${team.toLowerCase()}`, label: `Back to ${teams[team].name} intelligence` };
    if (from.startsWith("/?week=") && !/[\\\r\n]/.test(from))
      return { href: from, label: "Back to the slate" };
  }
  return { href: `/?week=${game.week}`, label: "Back to the slate" };
}
