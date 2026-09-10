import { performanceBands, type DiagnosticRecord } from "./performance-bands";

export type IntervalRecord = DiagnosticRecord & {
  marginInterval80: number[];
  totalInterval80: number[];
};

export function intervalCoverage(records: IntervalRecord[]) {
  const bands = performanceBands(records);
  const byId = new Map(records.map((r) => [r.id, r]));
  for (const r of records) {
    for (const bounds of [r.marginInterval80, r.totalInterval80]) {
      if (
        !Array.isArray(bounds) ||
        bounds.length !== 2 ||
        !bounds.every(Number.isFinite) ||
        bounds[0] > bounds[1]
      )
        throw new Error("Invalid outcome interval");
    }
  }
  function summarize(label: string, group: DiagnosticRecord[]) {
    const members = group.map((r) => byId.get(r.id)!);
    function outcome(
      interval: "marginInterval80" | "totalInterval80",
      actual: "actualMargin" | "actualTotal",
    ) {
      return {
        covered: members.filter(
          (r) => r[actual] >= r[interval][0] && r[actual] <= r[interval][1],
        ).length,
        meanWidth: members.length
          ? members.reduce(
              (sum, r) => sum + r[interval][1] - r[interval][0],
              0,
            ) / members.length
          : null,
      };
    }
    return {
      label,
      games: members.length,
      margin: outcome("marginInterval80", "actualMargin"),
      total: outcome("totalInterval80", "actualTotal"),
    };
  }
  return {
    all: summarize("All games", records),
    disagreement: bands.disagreement.map((b) => summarize(b.label, b.records)),
    missingMarket: bands.missingMarket,
  };
}
