type Role = {
  status: string;
  recordedAt: string | null;
  listedFirst: string | null;
  quarterbacks: { playerId: string; name: string; rank: number }[];
};
export type QuarterbackSnapshot = {
  season: number;
  retrievedAt: string;
  assetUpdatedAt: string;
  sourceUrl: string;
  sourceHash: string;
  teams: Record<string, Role>;
};
export function quarterbackForGame(
  snapshot: QuarterbackSnapshot,
  game: { season: number; kickoff: string | null; status: string },
  team: string,
  now = Date.now(),
) {
  const role = snapshot.teams[team];
  const kickoff = Date.parse(game.kickoff ?? "");
  const times = [
    snapshot.retrievedAt,
    snapshot.assetUpdatedAt,
    role?.recordedAt ?? "",
  ].map(Date.parse);
  if (
    game.status === "final" ||
    game.season !== snapshot.season ||
    !Number.isFinite(kickoff) ||
    now >= kickoff ||
    times.some(
      (t) =>
        !Number.isFinite(t) ||
        t > now ||
        t >= kickoff ||
        now - t >= 30 * 3600000,
    ) ||
    role?.status !== "available"
  )
    return null;
  const players = role.quarterbacks.filter(
    (p) => p.playerId === role.listedFirst && p.rank === 1,
  );
  if (!players.length || players.some((p) => p.name !== players[0].name))
    return null;
  return {
    name: players[0].name,
    recordedAt: role.recordedAt!,
    expiresAt: Math.min(kickoff, ...times.map((t) => t + 30 * 3600000)),
  };
}
