import { quotesForGame, type OddsFeed, type BookQuote } from "./odds";
export function selectRecentArchives(paths: string[]) {
  const groups = new Map<string, string[]>();
  let invalid = 0;
  for (const path of new Set(paths)) {
    if (
      !/^odds\/\d{4}-\d{2}-\d{2}\/\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d{3}Z-[a-f0-9]{64}\.json\.gz$/.test(
        path,
      )
    ) {
      invalid++;
      continue;
    }
    const stamp = path.replace(/-[a-f0-9]{64}\.json\.gz$/, "");
    groups.set(stamp, [...(groups.get(stamp) ?? []), path]);
  }
  const unique = [...groups.values()]
    .filter((g) => g.length === 1)
    .map((g) => g[0]);
  return {
    paths: unique.sort().slice(-12),
    conflicts: [...groups.values()].filter((g) => g.length > 1).length,
    invalid,
  };
}
export type HistoryObservation = { fetchedAt: string; books: BookQuote[] };
export type MarketHistory = {
  state: "ready" | "partial" | "unavailable";
  observations: HistoryObservation[];
};
export function historyForGame(
  feeds: OddsFeed[],
  game: { home: string; away: string; kickoff: string | null; status: string },
  now = Date.now(),
): HistoryObservation[] {
  const grouped = new Map<number, OddsFeed[]>();
  for (const feed of feeds) {
    const at = Date.parse(feed.fetchedAt);
    if (feed.state !== "ready" || !Number.isFinite(at) || at > now) continue;
    grouped.set(at, [...(grouped.get(at) ?? []), feed]);
  }
  const result: HistoryObservation[] = [];
  for (const [at, captures] of [...grouped].sort((a, b) => a[0] - b[0])) {
    if (new Set(captures.map((f) => JSON.stringify(f))).size !== 1) continue;
    const books = quotesForGame(
      captures[0],
      { ...game, status: "scheduled" },
      at,
    );
    if (books.length) result.push({ fetchedAt: captures[0].fetchedAt, books });
  }
  return result;
}
