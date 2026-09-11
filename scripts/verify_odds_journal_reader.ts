/** Read-only verification against the previously retained isolated storage probe. */
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { readBlob } from "../src/lib/odds-store";
import { readAttemptEvidence } from "../src/lib/odds-attempt-journal";

async function main() {
  const probe = JSON.parse(readFileSync("reviews/odds-journal-storage-verification.json", "utf8"));
  assert.match(probe.runId, /^[a-f0-9-]{36}$/);
  const prefix = `verification/odds-journal/${probe.runId}/`;
  const receipts = probe.receipts.filter((r: {path: string}) => r.path.startsWith(prefix + "odds/attempt-journal/"));
  assert.equal(receipts.length, 3);
  const match = receipts[0].path.match(/\/attempt-journal\/(\d+)\/reserved.json$/);
  assert.ok(match);
  const at = Number(match[1]);
  const read = async (path: string) => {
    const receipt = receipts.find((r: {path: string}) => r.path === prefix + path);
    assert.ok(receipt, "Read must match a retained probe receipt");
    const raw = await readBlob(receipt.path);
    assert.ok(raw, "Retained evidence missing");
    assert.equal(createHash("sha256").update(raw).digest("hex"), receipt.sha256);
    return raw;
  };
  const result = await readAttemptEvidence(at, read);
  assert.equal(result?.stage, "failed");
  assert.equal(result?.reason, "unknown-error");
  const report = { checkedAt: new Date().toISOString(), probeRunId: probe.runId,
    result, checks: ["three retained byte hashes verified", "complete event chain validated"],
    limitations: "Reads existing synthetic probe records only. No provider request, storage write, complete usage history or hosted execution established." };
  writeFileSync("reviews/odds-journal-reader-verification.json", JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report));
}
main().catch(() => { console.error("Journal reader verification failed"); process.exitCode = 1; });
