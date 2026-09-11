import { test } from "node:test";
import assert from "node:assert/strict";
import { recordAttemptEvent, readAttemptEvidence } from "../src/lib/odds-attempt-journal";

function store() {
  const files = new Map<string, Buffer>();
  const io = { read: async (path: string) => files.get(path) ?? null,
    write: async (path: string, body: Buffer) => {
      if (files.has(path)) throw new Error("already exists");
      files.set(path, body);
    } };
  return { files, io };
}
const reserved = { attemptStartedAt: 1000, eventAt: 1000, stage: "reserved" as const };
const requested = { ...reserved, eventAt: 1001, stage: "requested" as const };

test("reader distinguishes missing, unfinished and terminal evidence without writing", async () => {
  const { files, io } = store();
  assert.equal(await readAttemptEvidence(1000, io.read), null);
  await recordAttemptEvent(reserved, io);
  assert.equal((await readAttemptEvidence(1000, io.read))?.stage, "reserved");
  await recordAttemptEvent(requested, io);
  assert.equal((await readAttemptEvidence(1000, io.read))?.stage, "requested");
  await recordAttemptEvent({ ...requested, stage: "captured", eventAt: 1002, archiveSha256: "a".repeat(64) }, io);
  const result = await readAttemptEvidence(1000, io.read);
  assert.equal(result?.stage, "captured");
  assert.equal(result?.archiveSha256, "a".repeat(64));
  assert.equal(files.size, 3);
});

test("reader rejects damaged, foreign, orphaned and reversed events", async () => {
  for (const damage of ["null", "[]", "{", JSON.stringify({schemaVersion: 2, ...reserved}),
    JSON.stringify({schemaVersion: 1, ...reserved, attemptStartedAt: 999}),
    JSON.stringify({schemaVersion: 1, ...reserved, secret: "unexpected"})]) {
    const { files, io } = store();
    files.set("odds/attempt-journal/1000/reserved.json", Buffer.from(damage));
    await assert.rejects(readAttemptEvidence(1000, io.read));
  }
  const { files, io } = store();
  const first = await recordAttemptEvent(reserved, io);
  await recordAttemptEvent({ ...requested, eventAt: 1010 }, io);
  const last = await recordAttemptEvent({ ...requested, eventAt: 1011, stage: "failed", reason: "provider-error" }, io);
  assert.equal((await readAttemptEvidence(1000, io.read))?.reason, "provider-error");
  const validOutcome = files.get(last.path)!;
  files.set(last.path, Buffer.from(JSON.stringify({schemaVersion: 1, ...requested, eventAt: 1005, stage: "failed", reason: "provider-error"})));
  await assert.rejects(readAttemptEvidence(1000, io.read), /chronology/);
  files.set(last.path, validOutcome);
  files.delete(first.path);
  await assert.rejects(readAttemptEvidence(1000, io.read), /predecessor/);
});

test("reader validates identity before storage and propagates storage failure", async () => {
  for (const at of [-1, NaN, 1.5, Number.MAX_SAFE_INTEGER + 1])
    await assert.rejects(readAttemptEvidence(at, async () => { throw new Error("must not read"); }), /time/);
  await assert.rejects(readAttemptEvidence(1000, async () => { throw new Error("storage unavailable"); }), /storage unavailable/);
});

test("journal preserves event order and only records approved fields", async () => {
  const { files, io } = store();
  await recordAttemptEvent({ ...reserved, apiKey: "must-not-persist" } as typeof reserved, io);
  await recordAttemptEvent(requested, io);
  const end = { ...reserved, eventAt: 1002, stage: "captured" as const, archiveSha256: "a".repeat(64) };
  const first = await recordAttemptEvent(end, io);
  assert.deepEqual(await recordAttemptEvent(end, io), first);
  assert.equal(files.size, 3);
  assert.ok([...files.values()].every(b => !b.toString().includes("must-not-persist")));
  await assert.rejects(recordAttemptEvent({ ...reserved, eventAt: 1003, stage: "failed", reason: "provider-error" }, io), /conflict/i);
});

test("missing predecessor and reversed chronology cannot become valid evidence", async () => {
  const { io } = store();
  await assert.rejects(recordAttemptEvent(requested, io), /predecessor/i);
  await recordAttemptEvent(reserved, io);
  await assert.rejects(recordAttemptEvent({ ...requested, eventAt: 999 }, io), /time/i);
});

test("lost write response succeeds only after exact readback", async () => {
  const { io } = store();
  const write = io.write;
  io.write = async (path, body) => { await write(path, body); throw new Error("lost response"); };
  const receipt = await recordAttemptEvent(reserved, io);
  assert.match(receipt.sha256, /^[a-f0-9]{64}$/);
});

test("unverified write cannot report success", async () => {
  const { io } = store();
  io.write = async () => {};
  await assert.rejects(recordAttemptEvent(reserved, io), /readback/i);
});

test("idempotent replay still requires intact predecessor evidence", async () => {
  const { files, io } = store();
  const prior = await recordAttemptEvent(reserved, io);
  await recordAttemptEvent(requested, io);
  files.delete(prior.path);
  await assert.rejects(recordAttemptEvent(requested, io), /predecessor/i);
});

test("competing terminal outcomes retain exactly one immutable result", async () => {
  const { files, io } = store();
  await recordAttemptEvent(reserved, io);
  await recordAttemptEvent(requested, io);
  const results = await Promise.allSettled([
    recordAttemptEvent({ ...reserved, eventAt: 1002, stage: "captured", archiveSha256: "a".repeat(64) }, io),
    recordAttemptEvent({ ...reserved, eventAt: 1002, stage: "failed", reason: "provider-error" }, io),
  ]);
  assert.equal(results.filter(r => r.status === "fulfilled").length, 1);
  assert.equal(results.filter(r => r.status === "rejected").length, 1);
  assert.equal(files.size, 3);
});

test("malformed stored predecessors are rejected without writing a successor", async () => {
  for (const raw of ["null", "[]", "17", "{}", "not-json"]) {
    const { files, io } = store();
    files.set("odds/attempt-journal/1000/reserved.json", Buffer.from(raw));
    await assert.rejects(recordAttemptEvent(requested, io), /Invalid attempt journal predecessor/);
    assert.equal(files.size, 1);
  }
});

test("a terminal event cannot predate the verified request", async () => {
  const { files, io } = store();
  await recordAttemptEvent(reserved, io);
  await recordAttemptEvent({ ...requested, eventAt: 1010 }, io);
  await assert.rejects(recordAttemptEvent({ ...reserved, eventAt: 1005,
    stage: "failed", reason: "provider-error" }, io), /predecessor/);
  assert.equal(files.size, 2);
});
