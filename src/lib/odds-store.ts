import { get, put } from "@vercel/blob";
import { createHash, randomUUID } from "node:crypto";
import { gunzipSync } from "node:zlib";
import { prepareArchive } from "./odds-archive";
import { ODDS_MAX_AGE_MS, type OddsFeed } from "./odds";

const LATEST = "odds/latest.json";
const RESERVATION = "odds/acquisition-reservation.json";
export const ACQUISITION_COOLDOWN_MS = 30 * 60 * 1000;
type Reader = (path: string) => Promise<Buffer | null>;
type Writer = (
  path: string,
  body: Buffer,
  overwrite: boolean,
  ifMatch?: string,
) => Promise<void>;
type VersionReader = (
  path: string,
) => Promise<{ body: Buffer; etag: string } | null>;
const readBlobVersion: VersionReader = async (path) => {
  const result = await get(path, {
    access: "private",
    useCache: false,
    abortSignal: AbortSignal.timeout(5000),
  });
  if (!result) return null;
  if (result.statusCode !== 200 || result.blob.size > 2_000_000)
    throw new Error("Invalid stored odds object");
  return {
    body: Buffer.from(await new Response(result.stream).arrayBuffer()),
    etag: result.blob.etag,
  };
};
export const readBlob: Reader = async (path) =>
  (await readBlobVersion(path))?.body ?? null;
const writeBlob: Writer = async (path, body, overwrite, ifMatch) => {
  await put(path, body, {
    access: "private",
    allowOverwrite: overwrite,
    ifMatch,
    addRandomSuffix: false,
    contentType: path.endsWith(".gz") ? "application/gzip" : "application/json",
    abortSignal: AbortSignal.timeout(5000),
  });
};

export async function reserveOddsAcquisition(
  now: number,
  readVersion: VersionReader = readBlobVersion,
  write: Writer = writeBlob,
) {
  if (
    !Number.isSafeInteger(now) ||
    now < 0 ||
    !Number.isSafeInteger(now + ACQUISITION_COOLDOWN_MS)
  )
    throw new Error("Invalid acquisition clock");
  const current = await readVersion(RESERVATION);
  if (current) {
    if (!current.etag || current.body.length > 4096)
      throw new Error("Invalid acquisition reservation");
    const reservation = JSON.parse(current.body.toString());
    if (
      reservation.schemaVersion !== 1 ||
      !Number.isSafeInteger(reservation.startedAt) ||
      reservation.startedAt < 0 ||
      !Number.isSafeInteger(reservation.expiresAt) ||
      reservation.expiresAt - reservation.startedAt !== ACQUISITION_COOLDOWN_MS
    )
      throw new Error("Invalid acquisition reservation");
    if (now < reservation.expiresAt)
      throw new Error("Odds acquisition already reserved");
  }
  const expiresAt = now + ACQUISITION_COOLDOWN_MS;
  // Never release on failure: a timed-out provider request may have spent credits.
  // A lost reservation response also fails closed until this cooldown expires.
  await write(
    RESERVATION,
    Buffer.from(
      JSON.stringify({
        schemaVersion: 1,
        startedAt: now,
        expiresAt,
        owner: randomUUID(),
      }),
    ),
    current !== null,
    current?.etag,
  );
  return expiresAt;
}

export async function publishOdds(
  feed: OddsFeed,
  write: Writer = writeBlob,
  read: Reader = readBlob,
  readVersion: VersionReader = readBlobVersion,
) {
  const archive = prepareArchive(feed);
  try {
    await write(archive.pathname, archive.body, false);
  } catch (error) {
    // A previous attempt may have committed the immutable file before timing out.
    const existing = await read(archive.pathname);
    if (!existing || !existing.equals(archive.body)) throw error;
  }
  const current = await readVersion(LATEST);
  if (current) {
    if (!current.etag) throw new Error("Odds pointer version missing");
    const ref = parsePointer(current.body);
    const previousTime = Date.parse(ref.fetchedAt);
    const nextTime = Date.parse(feed.fetchedAt);
    if (previousTime > nextTime)
      throw new Error("Odds publication superseded by newer snapshot");
    if (previousTime === nextTime) {
      if (ref.sha256 !== archive.sha256)
        throw new Error("Conflicting odds acquisition timestamp");
      return {
        fetchedAt: feed.fetchedAt,
        sha256: archive.sha256,
        events: feed.events.length,
      };
    }
  }
  // Missing pointers use create-only; existing pointers require the exact read
  // version. A competing writer must never be overwritten without a fresh read.
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
    current !== null,
    current?.etag,
  );
  return {
    fetchedAt: feed.fetchedAt,
    sha256: archive.sha256,
    events: feed.events.length,
  };
}

function parsePointer(pointer: Buffer) {
  if (pointer.length > 16384) throw new Error("Invalid odds pointer");
  const ref = JSON.parse(pointer.toString());
  if (
    ref.schemaVersion !== 1 ||
    typeof ref.fetchedAt !== "string" ||
    !Number.isFinite(Date.parse(ref.fetchedAt)) ||
    typeof ref.sha256 !== "string" ||
    !/^[a-f0-9]{64}$/.test(ref.sha256) ||
    typeof ref.pathname !== "string" ||
    !/^odds\/\d{4}-\d{2}-\d{2}\/[A-Za-z0-9T.-]+-[a-f0-9]{64}\.json\.gz$/.test(
      ref.pathname,
    ) ||
    !ref.pathname.endsWith(`-${ref.sha256}.json.gz`)
  )
    throw new Error("Invalid odds pointer");
  return ref;
}

export async function readStoredOdds(
  read: Reader = readBlob,
): Promise<OddsFeed | null> {
  const pointer = await read(LATEST);
  if (!pointer) return null;
  const ref = parsePointer(pointer);
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
  if (feed?.state !== "ready") feed = null;
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
