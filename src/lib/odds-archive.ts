import { createHash } from "node:crypto";
import { gzipSync } from "node:zlib";
import { put } from "@vercel/blob";
import type { OddsFeed } from "./odds";

export function prepareArchive(feed: OddsFeed) {
  if (feed.state !== "ready" || !Number.isFinite(Date.parse(feed.fetchedAt)))
    throw new Error("Only successful timestamped feeds can be archived");
  const timestamp = new Date(feed.fetchedAt).toISOString();
  const content = Buffer.from(
    JSON.stringify({ schemaVersion: 1, provider: "The Odds API", feed }),
  );
  const sha256 = createHash("sha256").update(content).digest("hex");
  return {
    pathname: `odds/${timestamp.slice(0, 10)}/${timestamp.replaceAll(":", "-")}-${sha256}.json.gz`,
    body: gzipSync(content),
    sha256,
  };
}

type ArchiveWriter = (
  path: string,
  body: Buffer,
  options: {
    access: "private";
    allowOverwrite: false;
    addRandomSuffix: false;
    contentType: string;
    abortSignal: AbortSignal;
  },
) => Promise<{ pathname: string }>;

export async function archiveOdds(feed: OddsFeed, write: ArchiveWriter = put) {
  const archive = prepareArchive(feed);
  const result = await write(archive.pathname, archive.body, {
    access: "private",
    allowOverwrite: false,
    addRandomSuffix: false,
    contentType: "application/gzip",
    abortSignal: AbortSignal.timeout(5000),
  });
  return { pathname: result.pathname, sha256: archive.sha256 };
}
