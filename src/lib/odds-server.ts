import "server-only";
import { unstable_cache } from "next/cache";
import { readStoredOdds } from "./odds-store";
import type { OddsFeed } from "./odds";
// Page views in every environment read storage only; they never spend odds credits.
export const getOdds = unstable_cache(
  async (): Promise<OddsFeed> => {
    try {
      const feed = await readStoredOdds();
      if (feed) return feed;
    } catch {
      console.error("Stored odds unavailable");
    }
    return {
      state: "unavailable",
      fetchedAt: new Date().toISOString(),
      events: [],
    };
  },
  ["published-odds-v2"],
  { revalidate: 900, tags: ["published-odds"] },
);
