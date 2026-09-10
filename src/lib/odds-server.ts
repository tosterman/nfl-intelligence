import "server-only";
import { unstable_cache } from "next/cache";
import { createHash } from "node:crypto";
import { normalizeOdds, type OddsFeed } from "./odds";
export async function getOdds(): Promise<OddsFeed> {
  const key = process.env.ODDS_API_KEY;
  if (!key)
    return {
      state: "not-configured",
      fetchedAt: new Date().toISOString(),
      events: [],
    };
  // Only a one-way fingerprint enters the cache key. Never log request URLs/errors.
  const fingerprint = createHash("sha256").update(key).digest("hex");
  return unstable_cache(
    async () => {
      const fetchedAt = new Date().toISOString();
      try {
        const url = new URL(
          "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/",
        );
        url.search = new URLSearchParams({
          apiKey: key,
          regions: "us",
          markets: "h2h,spreads,totals",
          oddsFormat: "american",
        }).toString();
        const response = await fetch(url, {
          cache: "no-store",
          signal: AbortSignal.timeout(10000),
        });
        if (!response.ok) throw new Error("Provider unavailable");
        return normalizeOdds(await response.json(), new Date().toISOString());
      } catch {
        return { state: "unavailable", fetchedAt, events: [] } as OddsFeed;
      }
    },
    ["nfl-odds-v1", fingerprint],
    { revalidate: 21600 },
  )();
}
