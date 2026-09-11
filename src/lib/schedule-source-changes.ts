import evidence from "../../data/source-record-changes.json";

export function scheduleSourceChanges(gameId: string, before?: string, after?: string) {
  const pair = [evidence, ...evidence.additionalPairs].find(value =>
    before === value.beforeSha256 && after === value.afterSha256 && value.comparedSiteGames.includes(gameId));
  if (!pair) return null;
  const revision = pair.revisions.find(row => row.gameId === gameId);
  const fields = revision?.fields ?? [];
  const category = (field: string) => {
    if (["away_moneyline", "home_moneyline", "away_spread_odds", "home_spread_odds",
      "over_odds", "under_odds", "spread_line", "total_line"].includes(field)) return "Betting lines and prices";
    if (["away_qb_id", "away_qb_name", "home_qb_id", "home_qb_name"].includes(field)) return "Quarterback identity";
    return "Other schedule fields";
  };
  return { categories: [...new Set(fields.map(category))],
    olderCollectionTimeUnknown: pair === evidence,
    otherRecords: pair.changedRecords - (revision ? 1 : 0) };
}
