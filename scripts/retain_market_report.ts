import { get, put } from "@vercel/blob";
import { createHash } from "node:crypto";
import { readFile, writeFile, rm } from "node:fs/promises";
import { gunzipSync } from "node:zlib";

async function main() {
  const benchmark = process.argv[3] === '--benchmark';
  if(process.argv[3] && !benchmark)throw new Error('Unknown retention mode');
  const receiptPath=benchmark?"release-recovery/market-benchmark-retention.json":"release-recovery/market-audit-retention.json";
  const body = await readFile(process.argv[2]);
  if (body.length > 20_000_000) throw new Error("Bundle too large");
  const bundle = JSON.parse(
    gunzipSync(body, { maxOutputLength: 100_000_000 }).toString(),
  );
  const reportBytes = Buffer.from(bundle.files["report.json"].base64, "base64");
  const reportHash = createHash("sha256").update(reportBytes).digest("hex");
  if (bundle.schemaVersion !== 1 || reportHash !== bundle.reportHash)
    throw new Error("Invalid bundle");
  if(benchmark && bundle.kind !== 'market-benchmark')throw new Error('Wrong benchmark bundle');
  if(!benchmark && bundle.kind === 'market-benchmark')throw new Error('Benchmark mode required');
  const report = JSON.parse(reportBytes.toString());
  await rm(receiptPath,{force:true});
  const sha256 = createHash("sha256").update(body).digest("hex");
  const pathname = `${benchmark?'market-benchmarks':'market-audits'}/${sha256}.json.gz`;
  // Create-only; a pre-existing object is accepted only after exact readback.
  const existing = await get(pathname, {
    access: "private",
    useCache: false,
    abortSignal: AbortSignal.timeout(10000),
  });
  if (!existing)
    await put(pathname, body, {
      access: "private",
      addRandomSuffix: false,
      allowOverwrite: false,
      contentType: "application/gzip",
      abortSignal: AbortSignal.timeout(15000),
    });
  const verified = await get(pathname, {
    access: "private",
    useCache: false,
    abortSignal: AbortSignal.timeout(10000),
  });
  if (
    !verified ||
    verified.statusCode !== 200 ||
    verified.blob.size !== body.length
  )
    throw new Error("Retention readback failed");
  const retained = Buffer.from(
    await new Response(verified.stream).arrayBuffer(),
  );
  if (!retained.equals(body)) throw new Error("Retention bytes differ");
  const receipt = {
    schemaVersion: 1,
    status: "verified-private-retention",
    checkedAt: new Date().toISOString(),
    pathname,
    sha256,
    reportHash,
    bytes: body.length,
    uploadedAt: verified.blob.uploadedAt.toISOString(),
    coverageThrough: report.coverageThrough,
    checkpointCounts: benchmark?report.closingCheckpointCounts:report.checkpointCounts,
    marketCounts: report.marketCounts,
    ...(benchmark?{pairedGameCount:report.pairedGameCount}:{}),
  };
  await writeFile(
    receiptPath,
    JSON.stringify(receipt, null, 2) + "\n",
  );
  console.log(JSON.stringify(receipt));
}
main().catch(() => {
  console.error("Market report retention failed; no verified receipt written.");
  process.exitCode = 1;
});
