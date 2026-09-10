export function impliedProbability(odds: number): number {
  if (!Number.isFinite(odds) || Math.abs(odds) < 100)
    throw new Error("Invalid American odds");
  return odds < 0 ? -odds / (-odds + 100) : 100 / (odds + 100);
}
export function fairMoneyline(p: number): number {
  if (!Number.isFinite(p) || p <= 0 || p >= 1)
    throw new Error("Probability must be between zero and one");
  return Math.round(p > 0.5 ? (-100 * p) / (1 - p) : (100 * (1 - p)) / p);
}
export function noVig(home: number, away: number) {
  const h = impliedProbability(home),
    a = impliedProbability(away);
  return { home: h / (h + a), away: a / (h + a) };
}
export type Market = {
  homeSpread: number;
  total: number;
  homeMoneyline: number;
  awayMoneyline: number;
  observedAt: string;
};
export function compareMarket(
  prediction: { homeMargin: number; total: number; homeWinProbability: number },
  market: Market | null,
  asOf: string,
) {
  if (!market) return null;
  if (
    prediction.homeWinProbability <= 0 ||
    prediction.homeWinProbability >= 1 ||
    prediction.total <= 0 ||
    market.total <= 0
  )
    return null;
  const age = Date.parse(asOf) - Date.parse(market.observedAt);
  if (!Number.isFinite(age) || age < 0 || age > 60 * 60 * 1000) return null;
  if (
    ![
      prediction.homeMargin,
      prediction.total,
      prediction.homeWinProbability,
      market.homeSpread,
      market.total,
    ].every(Number.isFinite)
  )
    return null;
  try {
    return {
      spreadDifference: prediction.homeMargin + market.homeSpread,
      totalDifference: prediction.total - market.total,
      probabilityDifference:
        prediction.homeWinProbability -
        noVig(market.homeMoneyline, market.awayMoneyline).home,
    };
  } catch {
    return null;
  }
}
export function gradeSpread(homeMargin: number, homeSpread: number) {
  return homeMargin + homeSpread === 0
    ? "push"
    : homeMargin + homeSpread > 0
      ? "win"
      : "loss";
}
export function gradeTotal(
  total: number,
  line: number,
  side: "over" | "under",
) {
  return total === line
    ? "push"
    : total > line === (side === "over")
      ? "win"
      : "loss";
}
