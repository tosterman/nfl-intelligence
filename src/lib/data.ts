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
    logLoss: number | null;
    scoreGames: number;
    calibration: {
      lower: number;
      upper: number;
      count: number;
      predicted: number;
      observed: number;
      observedLow95: number;
      observedHigh95: number;
    }[];
    marginMae: number | null;
    totalMae: number | null;
    marginIntervalCoverage: number | null;
    totalIntervalCoverage: number | null;
    marginIntervalGames: number;
    totalIntervalGames: number;
    scoreRecords: {
      gameId: string;
      snapshotHash: string;
      generatedAt: string;
      homeMargin: number;
      total: number;
      actualMargin: number;
      actualTotal: number;
      marginError: number;
      totalError: number;
      marginCovered80: boolean | null;
      totalCovered80: boolean | null;
    }[];
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
