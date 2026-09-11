import { createHash, timingSafeEqual } from "node:crypto";
import { normalizeOdds, type OddsFeed } from "./odds";
import { prepareArchive } from "./odds-archive";
import type { recordAttemptEvent } from "./odds-attempt-journal";
import {
  publishOdds,
  readStoredOdds,
  oddsHealth,
  reserveOddsAcquisition,
} from "./odds-store";
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
    reserve: reserveOddsAcquisition,
  });
}
export async function runOddsCollection({
  key,
  read,
  publish,
  fetcher,
  now,
  reserve,
  reuse = canReuseSnapshot,
  journal,
  beforeRequest,
}: {
  key: string | undefined;
  read: () => Promise<OddsFeed | null>;
  publish: (
    feed: OddsFeed,
  ) => Promise<{ fetchedAt: string; sha256: string; events: number }>;
  fetcher: typeof fetch;
  now: () => number;
  reserve: (now: number) => Promise<number>;
  reuse?: typeof canReuseSnapshot;
  journal?: (
    event: Parameters<typeof recordAttemptEvent>[0],
  ) => Promise<unknown>;
  beforeRequest?: () => Promise<void>;
}) {
  if (!key) throw new Error("Collection configuration missing");
  const existing = await read();
  const health = oddsHealth(existing, now());
  if (reuse(existing, now())) return { ...health, status: "already-current" };
  // /sports is quota-free and reports current account credits. Do not guess
  // availability from a previous snapshot or assume a calendar reset date.
  const quotaUrl = new URL("https://api.the-odds-api.com/v4/sports/");
  quotaUrl.search = new URLSearchParams({ apiKey: key }).toString();
  const quotaResponse = await fetcher(quotaUrl, {
    cache: "no-store",
    redirect: "error",
    signal: AbortSignal.timeout(10000),
  });
  const remaining = quotaResponse.headers.get("x-requests-remaining");
  await quotaResponse.body?.cancel();
  if (
    !quotaResponse.ok ||
    remaining === null ||
    !/^\d+$/.test(remaining) ||
    !Number.isSafeInteger(Number(remaining)) ||
    Number(remaining) < 3
  )
    throw new Error("Odds quota unavailable or insufficient");
  const reservedAt = now();
  const expiresAt = await reserve(reservedAt);
  await journal?.({
    attemptStartedAt: reservedAt,
    eventAt: reservedAt,
    stage: "reserved",
  });
  const checkReservation = () => {
    if (
      !Number.isSafeInteger(expiresAt) ||
      now() < reservedAt ||
      now() >= expiresAt
    )
      throw new Error("Odds acquisition reservation expired");
  };
  checkReservation();
  // This records dispatch intent, not proof that the provider received it.
  await journal?.({
    attemptStartedAt: reservedAt,
    eventAt: now(),
    stage: "requested",
  });
  await beforeRequest?.();
  checkReservation();
  const url = new URL(
    "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/",
  );
  url.search = new URLSearchParams({
    apiKey: key,
    regions: "us",
    markets: "h2h,spreads,totals",
    oddsFormat: "american",
  }).toString();
  let reason: "provider-error" | "storage-error" | "readback-error" =
    "provider-error";
  let evidence;
  let creditsRemaining: string | null;
  try {
    const response = await fetcher(url, {
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(10000),
    });
    if (!response.ok) throw new Error("Odds acquisition failed");
    const feed = normalizeOdds(
      await response.json(),
      new Date(now()).toISOString(),
    );
    creditsRemaining = response.headers.get("x-requests-remaining");
    reason = "storage-error";
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        evidence = await publish(feed);
        break;
      } catch {
        if (attempt === 2) throw new Error("Odds storage failed");
      }
    }
    reason = "readback-error";
    const saved = await read();
    if (
      !saved ||
      oddsHealth(saved, now()).status !== "ok" ||
      prepareArchive(saved).sha256 !== evidence?.sha256
    )
      throw new Error("Odds readback failed");
  } catch (error) {
    // A failure to record an outcome must not trigger another acquisition.
    // Propagate that uncertainty instead of claiming a persisted failure.
    await journal?.({
      attemptStartedAt: reservedAt,
      eventAt: now(),
      stage: "failed",
      reason,
    });
    throw error;
  }
  // Outside the catch: an uncertain captured write cannot become a competing
  // failure outcome. The journal itself resolves lost responses by readback.
  await journal?.({
    attemptStartedAt: reservedAt,
    eventAt: now(),
    stage: "captured",
    archiveSha256: evidence?.sha256,
  });
  return {
    status: "captured",
    ...evidence,
    creditsRemaining,
  };
}
