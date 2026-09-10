export type DiagnosticRecord = {
  id: string;
  season: number;
  week: number;
  homeWinProbability: number;
  homeMargin: number;
  total: number;
  actualMargin: number;
  actualTotal: number;
  marketMargin: number | null;
};
function summarize(label: string, records: DiagnosticRecord[]) {
  const decisive = records.filter((r) => r.actualMargin !== 0);
  const selections = records.filter(
    (r) => r.marketMargin != null && r.homeMargin !== r.marketMargin,
  );
  const settlement = (r: DiagnosticRecord) =>
    Math.sign(r.homeMargin - r.marketMargin!) *
    Math.sign(r.actualMargin - r.marketMargin!);
  const mean = (f: (r: DiagnosticRecord) => number) =>
    records.length
      ? records.reduce((sum, r) => sum + f(r), 0) / records.length
      : null;
  return {
    label,
    records,
    decisive: decisive.length,
    ties: records.length - decisive.length,
    correct: decisive.filter(
      (r) => r.homeWinProbability >= 0.5 === r.actualMargin > 0,
    ).length,
    marginMae: mean((r) => Math.abs(r.homeMargin - r.actualMargin)),
    totalMae: mean((r) => Math.abs(r.total - r.actualTotal)),
    wins: selections.filter((r) => settlement(r) > 0).length,
    losses: selections.filter((r) => settlement(r) < 0).length,
    pushes: selections.filter((r) => settlement(r) === 0).length,
    noDirection: records.filter(
      (r) => r.marketMargin != null && r.homeMargin === r.marketMargin,
    ).length,
  };
}
export function performanceBands(records: DiagnosticRecord[]) {
  const ids = new Set<string>();
  for (const r of records) {
    if (
      !r.id ||
      ids.has(r.id) ||
      ![
        r.homeWinProbability,
        r.homeMargin,
        r.total,
        r.actualMargin,
        r.actualTotal,
      ].every(Number.isFinite) ||
      r.homeWinProbability < 0 ||
      r.homeWinProbability > 1 ||
      (r.marketMargin != null && !Number.isFinite(r.marketMargin))
    )
      throw new Error("Invalid diagnostic record");
    ids.add(r.id);
  }
  const confidenceCuts = [0.5, 0.6, 0.7, 0.8, 1.01];
  const disagreementCuts = [0, 2, 4, 6, Infinity];
  return {
    confidence: ["50–<60%", "60–<70%", "70–<80%", "80–100%"].map((label, i) =>
      summarize(
        label,
        records.filter((r) => {
          const p = Math.max(r.homeWinProbability, 1 - r.homeWinProbability);
          return p >= confidenceCuts[i] && p < confidenceCuts[i + 1];
        }),
      ),
    ),
    disagreement: [
      "0–<2 points",
      "2–<4 points",
      "4–<6 points",
      "6+ points",
    ].map((label, i) =>
      summarize(
        label,
        records.filter((r) => {
          if (r.marketMargin == null) return false;
          const distance = Math.abs(r.homeMargin - r.marketMargin);
          return (
            distance >= disagreementCuts[i] &&
            distance < disagreementCuts[i + 1]
          );
        }),
      ),
    ),
    missingMarket: records.filter((r) => r.marketMargin == null).length,
  };
}
