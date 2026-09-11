import "server-only";
import { unstable_cache } from "next/cache";
import { readStoredOdds } from "./odds-store";
import type { OddsFeed } from "./odds";
// Page views in every environment read storage only; they never spend odds credits.
const getPublishedOdds = unstable_cache(
  async (): Promise<OddsFeed> => {
    const feed = await readStoredOdds();
    if (!feed) throw new Error('Stored odds unavailable');
    return feed;
  },
  ["published-odds-v2"],
  { revalidate: 900, tags: ["published-odds"] },
);

// Cache verified data, not a transient read failure for the full 15-minute window.
// Existing quote/source deadlines still apply when Next serves a retained value.
export async function getOdds(): Promise<OddsFeed> {
  try { return await getPublishedOdds(); }
  catch {
    console.error('Stored odds unavailable');
    return { state: 'unavailable', fetchedAt: new Date().toISOString(), events: [] };
  }
}
