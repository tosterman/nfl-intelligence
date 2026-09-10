import { createHash, timingSafeEqual } from "node:crypto";
import { normalizeOdds, type OddsFeed } from "./odds";
import { prepareArchive } from "./odds-archive";
import { publishOdds, readStoredOdds, oddsHealth } from "./odds-store";
export function authorizedCollector(
  header: string | null,
  secret: string | undefined,
) {
  if (!secret || secret.length < 32 || !header) return false;
  return timingSafeEqual(
    createHash("sha256").update(header).digest(),
    createHash("sha256").update(`Bearer ${secret}`).digest(),
  );
}
export function canReuseSnapshot(feed: OddsFeed | null, now = Date.now()) {
  const health = oddsHealth(feed, now);
  // The next scheduled job is at most five hours away; retain freshness headroom.
  return (
    health.status === "ok" && health.ageHours !== null && health.ageHours < 0.5
  );
}
export async function collectOdds() {
  return runOddsCollection({
    key: process.env.ODDS_API_KEY,
    read: readStoredOdds,
    publish: publishOdds,
    fetcher: fetch,
    now: Date.now,
  });
}
export async function runOddsCollection({
  key,
  read,
  publish,
  fetcher,
  now,
}: {
  key: string | undefined;
  read: () => Promise<OddsFeed | null>;
  publish: (
    feed: OddsFeed,
  ) => Promise<{ fetchedAt: string; sha256: string; events: number }>;
  fetcher: typeof fetch;
  now: () => number;
}) {
  if (!key) throw new Error("Collection configuration missing");
  const existing = await read();
  const health = oddsHealth(existing, now());
  if (canReuseSnapshot(existing, now()))
    return { ...health, status: "already-current" };
  const url = new URL(
    "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/",
  );
  url.search = new URLSearchParams({
    apiKey: key,
    regions: "us",
    markets: "h2h,spreads,totals",
    oddsFormat: "american",
  }).toString();
  const response = await fetcher(url, {
    cache: "no-store",
    signal: AbortSignal.timeout(10000),
  });
  if (!response.ok) throw new Error("Odds acquisition failed");
  const feed = normalizeOdds(
    await response.json(),
    new Date(now()).toISOString(),
  );
  let evidence;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      evidence = await publish(feed);
      break;
    } catch {
      if (attempt === 2) throw new Error("Odds storage failed");
    }
  }
  const saved = await read();
  if (
    !saved ||
    oddsHealth(saved, now()).status !== "ok" ||
    prepareArchive(saved).sha256 !== evidence?.sha256
  )
    throw new Error("Odds readback failed");
  return {
    status: "captured",
    ...evidence,
    creditsRemaining: response.headers.get("x-requests-remaining"),
  };
}
