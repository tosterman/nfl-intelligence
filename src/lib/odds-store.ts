import { get, put } from "@vercel/blob";
import { createHash } from "node:crypto";
import { gunzipSync } from "node:zlib";
import { prepareArchive } from "./odds-archive";
import { ODDS_MAX_AGE_MS, type OddsFeed } from "./odds";

const LATEST = "odds/latest.json";
type Reader = (path: string) => Promise<Buffer | null>;
type Writer = (path: string, body: Buffer, overwrite: boolean) => Promise<void>;
export const readBlob: Reader = async (path) => {
  const result = await get(path, {
    access: "private",
    useCache: false,
    abortSignal: AbortSignal.timeout(5000),
  });
  if (!result) return null;
  if (result.statusCode !== 200 || result.blob.size > 2_000_000)
    throw new Error("Invalid stored odds object");
  return Buffer.from(await new Response(result.stream).arrayBuffer());
};
const writeBlob: Writer = async (path, body, overwrite) => {
  await put(path, body, {
    access: "private",
    allowOverwrite: overwrite,
    addRandomSuffix: false,
    contentType: path.endsWith(".gz") ? "application/gzip" : "application/json",
    abortSignal: AbortSignal.timeout(5000),
  });
};

export async function publishOdds(
  feed: OddsFeed,
  write: Writer = writeBlob,
  read: Reader = readBlob,
) {
  const archive = prepareArchive(feed);
  try {
    await write(archive.pathname, archive.body, false);
  } catch (error) {
    // A previous attempt may have committed the immutable file before timing out.
    const existing = await read(archive.pathname);
    if (!existing || !existing.equals(archive.body)) throw error;
  }
  await write(
    LATEST,
    Buffer.from(
      JSON.stringify({
        schemaVersion: 1,
        pathname: archive.pathname,
        sha256: archive.sha256,
        fetchedAt: feed.fetchedAt,
      }),
    ),
    true,
  );
  return {
    fetchedAt: feed.fetchedAt,
    sha256: archive.sha256,
    events: feed.events.length,
  };
}

export async function readStoredOdds(
  read: Reader = readBlob,
): Promise<OddsFeed | null> {
  const pointer = await read(LATEST);
  if (!pointer) return null;
  if (pointer.length > 16384) throw new Error("Invalid odds pointer");
  const ref = JSON.parse(pointer.toString());
  if (
    ref.schemaVersion !== 1 ||
    typeof ref.sha256 !== "string" ||
    !/^[a-f0-9]{64}$/.test(ref.sha256) ||
    typeof ref.pathname !== "string" ||
    !/^odds\/\d{4}-\d{2}-\d{2}\/[A-Za-z0-9T.-]+-[a-f0-9]{64}\.json\.gz$/.test(
      ref.pathname,
    ) ||
    !ref.pathname.endsWith(`-${ref.sha256}.json.gz`)
  )
    throw new Error("Invalid odds pointer");
  const compressed = await read(ref.pathname);
  if (!compressed) throw new Error("Odds snapshot missing");
  const content = gunzipSync(compressed, { maxOutputLength: 10_000_000 });
  if (createHash("sha256").update(content).digest("hex") !== ref.sha256)
    throw new Error("Odds snapshot integrity failure");
  const envelope = JSON.parse(content.toString());
  const feed = envelope.feed;
  if (
    envelope.schemaVersion !== 1 ||
    envelope.provider !== "The Odds API" ||
    feed?.state !== "ready" ||
    feed.fetchedAt !== ref.fetchedAt ||
    !Number.isFinite(Date.parse(feed.fetchedAt)) ||
    !Array.isArray(feed.events)
  )
    throw new Error("Invalid odds snapshot");
  return feed;
}

export function oddsHealth(feed: OddsFeed | null, now = Date.now()) {
  const ageMs = feed ? now - Date.parse(feed.fetchedAt) : NaN;
  const status =
    !feed || feed.state !== "ready" || !Number.isFinite(ageMs) || ageMs < 0
      ? "unavailable"
      : ageMs > ODDS_MAX_AGE_MS
        ? "stale"
        : "ok";
  return {
    status,
    fetchedAt: feed?.fetchedAt ?? null,
    ageHours: Number.isFinite(ageMs) && ageMs >= 0 ? ageMs / 3600000 : null,
  };
}
