import type { PersonnelSnapshot, PlayerReport } from "./personnel";
import { teams } from "./teams";
const object = (value: unknown): Record<string, unknown> | null =>
  value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;

export function usageForPlayer(
  raw: unknown,
  snapshot: PersonnelSnapshot,
  player: PlayerReport,
  now = Date.now(),
) {
  const data = object(raw);
  if (
    !data ||
    data.schemaVersion !== 1 ||
    data.personnelSourceHash !== snapshot.sourceHash ||
    data.personnelRetrievedAt !== snapshot.retrievedAt ||
    !Array.isArray(data.records)
  )
    return null;
  const calculated = Date.parse(String(data.calculatedAt)),
    acquired = Date.parse(snapshot.retrievedAt);
  if (
    !Number.isFinite(calculated) ||
    !Number.isFinite(acquired) ||
    !Number.isFinite(now) ||
    calculated < acquired ||
    calculated > now ||
    !Number.isInteger(data.sourceSeason) ||
    Number(data.sourceSeason) >= player.season
  )
    return null;
  const matching = data.records
    .map(object)
    .filter(
      (r) =>
        r &&
        ["playerId", "team", "season", "type", "week"].every(
          (k) => r[k] === player[k as keyof PlayerReport],
        ),
    );
  if (
    matching.length !== 1 ||
    matching[0]!.name !== player.name ||
    matching[0]!.identityStatus !== "matched"
  )
    return null;
  const usage = object(matching[0]!.usage),
    shares = object(usage?.weightedShares);
  if (
    !usage ||
    usage.status !== "available" ||
    !shares ||
    !Number.isInteger(usage.appearances) ||
    Number(usage.appearances) < 1 ||
    Number(usage.appearances) > 8 ||
    !Array.isArray(usage.historicalTeams) ||
    !usage.historicalTeams.length ||
    !usage.historicalTeams.every(
      (t) => typeof t === "string" && Object.hasOwn(teams, t),
    )
  )
    return null;
  const last = Date.parse(String(usage.lastAppearance));
  if (
    !Number.isFinite(last) ||
    last + 24 * 3600000 >= calculated ||
    !["offense_pct", "defense_pct", "st_pct"].every(
      (k) =>
        typeof shares[k] === "number" &&
        Number.isFinite(shares[k]) &&
        Number(shares[k]) >= 0 &&
        Number(shares[k]) <= 1,
    )
  )
    return null;
  return {
    season: Number(data.sourceSeason),
    appearances: Number(usage.appearances),
    lastAppearance: String(usage.lastAppearance),
    historicalTeams: usage.historicalTeams as string[],
    shares: {
      offense_pct: Number(shares.offense_pct),
      defense_pct: Number(shares.defense_pct),
      st_pct: Number(shares.st_pct),
    },
  };
}
