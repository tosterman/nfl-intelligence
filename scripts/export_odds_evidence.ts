import { get, list } from "@vercel/blob";
import { createHash } from "node:crypto";
import { mkdir, mkdtemp, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { decodeArchive } from "../src/lib/odds-archive";

async function main() {
  const startedAt = new Date();
  const paths = new Set<string>();
  let cursor: string | undefined;
  const cursors = new Set<string>();
  do {
    const page = await list({
      prefix: "odds/",
      limit: 1000,
      cursor,
      abortSignal: AbortSignal.timeout(10000),
    });
    for (const blob of page.blobs) {
      if (
        /^odds\/\d{4}-\d{2}-\d{2}\/.*-[a-f0-9]{64}\.json\.gz$/.test(
          blob.pathname,
        ) &&
        blob.uploadedAt <= startedAt
      )
        paths.add(blob.pathname);
    }
    if (!page.hasMore) break;
    if (!page.cursor || cursors.has(page.cursor) || paths.size > 10000)
      throw new Error("Incomplete archive listing");
    cursor = page.cursor;
    cursors.add(cursor);
  } while (true);
  await mkdir("release-recovery", { recursive: true });
  const folder = await mkdtemp(join("release-recovery", "odds-evidence-"));
  const captures = [];
  for (const pathname of [...paths].sort()) {
    const response = await get(pathname, {
      access: "private",
      useCache: false,
      abortSignal: AbortSignal.timeout(10000),
    });
    if (
      !response ||
      response.statusCode !== 200 ||
      response.blob.size > 2_000_000 ||
      response.blob.uploadedAt > startedAt
    )
      throw new Error("Archive changed or unavailable during export");
    const body = Buffer.from(await new Response(response.stream).arrayBuffer());
    decodeArchive(body, pathname);
    const compressedHash = createHash("sha256").update(body).digest("hex");
    const filename = compressedHash + ".json.gz";
    await writeFile(join(folder, filename), body);
    captures.push({
      pathname,
      filename,
      compressedHash,
      uploadedAt: response.blob.uploadedAt.toISOString(),
      etag: response.blob.etag,
    });
  }
  await writeFile(
    join(folder, "manifest.json"),
    JSON.stringify(
      {
        schemaVersion: 1,
        startedAt: startedAt.toISOString(),
        exportedAt: new Date().toISOString(),
        source: "Authenticated private Vercel Blob",
        complete: true,
        captures,
      },
      null,
      2,
    ) + "\n",
  );
  console.log(JSON.stringify({ folder, captures: captures.length }));
}
main().catch(() => {
  console.error("Odds evidence export failed; no complete manifest accepted.");
  process.exitCode = 1;
});
