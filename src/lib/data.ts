import raw from "../../data/site.json";
import type { Game } from "./types";
export const site = {
  ...raw,
  games: raw.games as unknown as Game[],
  livePerformance: raw.livePerformance as {
    games: number;
    wins: number;
    ties: number;
    missed: number;
    brier: number | null;
    records: {
      gameId: string;
      snapshotHash: string;
      probability: number;
      outcome: number;
      correct: number;
      brier: number;
    }[];
  },
};
export type { Game, Prediction } from "./types";
export { teams, pct, signed, time, date } from "./teams";
