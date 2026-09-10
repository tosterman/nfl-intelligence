export type FreshnessInput = { name: string; retrievedAt?: string };
export const MAX_AGE_HOURS = 30;

export function assessFreshness(inputs: FreshnessInput[], now = Date.now()) {
  const checks = inputs.map((input) => {
    const timestamp = Date.parse(input.retrievedAt ?? "");
    const age = (now - timestamp) / 3600000;
    const valid = Number.isFinite(age) && age >= -5 / 60;
    return {
      name: input.name,
      retrievedAt: input.retrievedAt ?? null,
      ageHours: valid ? Math.max(0, Math.round(age * 10) / 10) : null,
      status: !valid ? "invalid" : age > MAX_AGE_HOURS ? "stale" : "ok",
    };
  });
  return {
    status:
      checks.length && checks.every((c) => c.status === "ok") ? "ok" : "stale",
    checks,
  };
}

export function freshnessInputs(site: {
  season: number;
  generatedAt: string;
  source: { retrievedAt?: string };
  efficiencySources: { season: number; retrievedAt?: string }[];
}): FreshnessInput[] {
  return [
    { name: "Model edition", retrievedAt: site.generatedAt },
    { name: "Schedule and results", retrievedAt: site.source.retrievedAt },
    ...[site.season - 1, site.season].map((season) => ({
      name: `${season} efficiency source`,
      retrievedAt: site.efficiencySources.find(
        (source) => source.season === season,
      )?.retrievedAt,
    })),
  ];
}
