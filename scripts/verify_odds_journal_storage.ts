/** Explicit live storage probe. No provider requests or production ledger writes. */
import assert from "node:assert/strict";
import { randomUUID, createHash } from "node:crypto";
import { writeFileSync } from "node:fs";
import { put } from "@vercel/blob";
import { readBlob } from "../src/lib/odds-store";
import { recordAttemptEvent } from "../src/lib/odds-attempt-journal";

async function main() {
  if (!process.argv.includes("--run-live")) throw new Error("Explicit --run-live required");
  const runId = randomUUID();
  const prefix = `verification/odds-journal/${runId}/`;
  const at = Date.now();
  const receipts: { path: string; sha256: string }[] = [];
  let simulateLostResponse = true;
  const write = async (path: string, body: Buffer) => {
    await put(prefix + path, body, { access: "private", allowOverwrite: false,
      addRandomSuffix: false, contentType: "application/json", abortSignal: AbortSignal.timeout(5000) });
  };
  const io = {
    read: (path: string) => readBlob(prefix + path),
    write: async (path: string, body: Buffer) => {
      await write(path, body);
      if (simulateLostResponse) { simulateLostResponse = false; throw new Error("Simulated lost response"); }
    },
  };
  const reserved = { attemptStartedAt: at, eventAt: at, stage: "reserved" as const };
  receipts.push(await recordAttemptEvent(reserved, io));
  // Bypass the journal's pre-read to exercise the service's create-only behavior.
  const isExistingObjectError = (error: unknown) => error instanceof Error &&
    /already exists|allowOverwrite/i.test(error.message);
  await assert.rejects(write(receipts[0].path, Buffer.from("conflicting probe")), isExistingObjectError);
  const retained = await io.read(receipts[0].path);
  assert.ok(retained);
  assert.equal(createHash("sha256").update(retained).digest("hex"), receipts[0].sha256);
  receipts.push(await recordAttemptEvent({ ...reserved, eventAt: Date.now(), stage: "requested" }, io));
  // Synthetic failure outcome deliberately avoids a fabricated capture digest.
  const failed = { ...reserved, eventAt: Date.now(), stage: "failed" as const, reason: "unknown-error" as const };
  const terminal = await recordAttemptEvent(failed, io);
  receipts.push(terminal);
  assert.deepEqual(await recordAttemptEvent(failed, io), terminal);
  await assert.rejects(recordAttemptEvent({ ...failed, reason: "provider-error" }, io), /conflict/i);
  for (const receipt of receipts) {
    const body = await io.read(receipt.path);
    assert.ok(body);
    assert.equal(createHash("sha256").update(body).digest("hex"), receipt.sha256);
  }
  const racePath = "concurrent-create.json";
  const contenders = [Buffer.from('{"probe":"A"}'), Buffer.from('{"probe":"B"}')];
  const raced = await Promise.allSettled(contenders.map(body => write(racePath, body)));
  assert.equal(raced.filter(result => result.status === "fulfilled").length, 1);
  assert.equal(raced.filter(result => result.status === "rejected").length, 1);
  const rejected = raced.find(result => result.status === "rejected");
  assert.ok(rejected?.status === "rejected" && isExistingObjectError(rejected.reason));
  const winner = contenders[raced.findIndex(result => result.status === "fulfilled")];
  assert.ok((await io.read(racePath))?.equals(winner));
  receipts.push({ path: racePath, sha256: createHash("sha256").update(winner).digest("hex") });
  const report = { checkedAt: new Date().toISOString(), runId,
    result: "passed", execution: "local Node process against actual private Vercel Blob",
    checks: ["create-only write rejection", "unchanged bytes after rejected overwrite",
      "readback after simulated lost response", "ordered event persistence", "idempotent replay",
      "conflicting terminal rejection", "final digest verification", "concurrent create admits exactly one writer"],
    receipts: receipts.map(r => ({ ...r, path: prefix + r.path })),
    limitations: "Synthetic isolated records. No provider requests, production reservations, serverless execution or scheduling verified. Lost response was injected after a real successful write." };
  writeFileSync("reviews/odds-journal-storage-verification.json", JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report));
}

main().catch(() => { console.error("Live journal storage verification failed; inspect private probe records before retrying."); process.exitCode = 1; });
