import "server-only";
import { unstable_cache } from "next/cache";
import { list } from "@vercel/blob";
import { readBlob } from "./odds-store";
import { decodeArchive } from "./odds-archive";
import {
  historyForGame,
  selectRecentArchives,
  type MarketHistory,
} from "./odds-history";
import type { OddsFeed } from "./odds";

// One shared cache across matchups; refreshed on collection, not per game visit.
const recentArchives = unstable_cache(
  async () => {
    const now = new Date(),
      paths: string[] = [];
    let partial = false;
    const listings = await Promise.allSettled(
      [0, 1, 2].map(async (offset) => {
        const day = new Date(now.getTime() - offset * 86400000)
          .toISOString()
          .slice(0, 10);
        return list({
          prefix: `odds/${day}/`,
          limit: 100,
          abortSignal: AbortSignal.timeout(5000),
        });
      }),
    );
    for (const result of listings) {
      if (result.status === "fulfilled") {
        const page = result.value;
        if (page.hasMore) {
          partial = true;
          continue;
        } // Never pretend a truncated listing is complete.
        paths.push(
          ...page.blobs
            .map((b) => b.pathname)
            .filter((p) => /\.json\.gz$/.test(p)),
        );
      } else {
        partial = true;
      }
    }
    const feeds: OddsFeed[] = [];
    const selection = selectRecentArchives(paths);
    partial ||= selection.conflicts > 0 || selection.invalid > 0;
    const selected = selection.paths;
    // Batch at most twelve small immutable objects; no raw archives enter client props.
    const results = await Promise.allSettled(
      selected.map(async (path) => {
        const compressed = await readBlob(path);
        if (!compressed) throw new Error("Missing history archive");
        return decodeArchive(compressed, path);
      }),
    );
    for (const result of results) {
      if (result.status === "fulfilled") feeds.push(result.value);
      else partial = true;
    }
    return { feeds, partial };
  },
  ["recent-odds-history-v1"],
  { revalidate: 21600, tags: ["published-odds"] },
);

export async function getMarketHistory(game: {
  home: string;
  away: string;
  kickoff: string | null;
  status: string;
}): Promise<MarketHistory> {
  const result = await recentArchives();
  return {
    state: result.partial
      ? result.feeds.length
        ? "partial"
        : "unavailable"
      : "ready",
    observations: historyForGame(result.feeds, game),
  };
}
