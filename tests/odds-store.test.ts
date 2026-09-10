import { createHash } from "node:crypto";
import { test } from "node:test";
import assert from "node:assert/strict";
import { publishOdds, readStoredOdds, oddsHealth } from "../src/lib/odds-store";
import type { OddsFeed } from "../src/lib/odds";
const feed: OddsFeed = {
  state: "ready",
  fetchedAt: "2026-09-10T17:00:00Z",
  events: [],
};
const fixture = () => {
  const files = new Map<string, Buffer>();
  return {
    files,
    read: async (path: string) => files.get(path) ?? null,
    readVersion: async (path: string) => {
      const body = files.get(path);
      return body
        ? { body, etag: createHash("sha256").update(body).digest("hex") }
        : null;
    },
    write: async (
      path: string,
      body: Buffer,
      overwrite: boolean,
      ifMatch?: string,
    ) => {
      if (
        ifMatch &&
        (!files.has(path) ||
          createHash("sha256").update(files.get(path)!).digest("hex") !==
            ifMatch)
      )
        throw new Error("precondition failed");
      if (files.has(path) && !overwrite) throw new Error("exists");
      files.set(path, body);
    },
  };
};
test("published pointer resolves only to an intact archived snapshot", async () => {
  const s = fixture();
  await publishOdds(feed, s.write, s.read, s.readVersion);
  assert.deepEqual(await readStoredOdds(s.read), feed);
  const path = [...s.files.keys()].find((p) => p.endsWith(".gz"))!;
  s.files.set(path, Buffer.from("corrupted"));
  await assert.rejects(readStoredOdds(s.read));
});
test("failed archive cannot advance pointer; retry after partial success is safe", async () => {
  const s = fixture();
  await assert.rejects(
    publishOdds(
      feed,
      async () => {
        throw new Error("offline");
      },
      s.read,
      s.readVersion,
    ),
  );
  assert.equal(s.files.size, 0);
  let fail = true;
  const write = async (p: string, b: Buffer, o: boolean, etag?: string) => {
    if (p.endsWith("latest.json") && fail) {
      fail = false;
      throw new Error("pointer failed");
    }
    await s.write(p, b, o, etag);
  };
  await assert.rejects(publishOdds(feed, write, s.read, s.readVersion));
  assert.equal(await readStoredOdds(s.read), null);
  await publishOdds(feed, write, s.read, s.readVersion);
  assert.deepEqual(await readStoredOdds(s.read), feed);
});
test("pointer cannot request external or unrelated objects", async () => {
  const s = fixture();
  s.files.set(
    "odds/latest.json",
    Buffer.from(
      JSON.stringify({
        schemaVersion: 1,
        pathname: "https://example.org/file",
        sha256: "a".repeat(64),
        fetchedAt: feed.fetchedAt,
      }),
    ),
  );
  await assert.rejects(readStoredOdds(s.read));
});
test("health rejects missing, future, and stale acquisitions", () => {
  const now = Date.parse(feed.fetchedAt);
  assert.equal(oddsHealth(feed, now).status, "ok");
  assert.equal(oddsHealth(feed, now + 6 * 3600000 + 1).status, "stale");
  assert.equal(oddsHealth(feed, now - 1).status, "unavailable");
  assert.equal(oddsHealth(null, now).status, "unavailable");
  assert.equal(
    oddsHealth({ ...feed, state: "unavailable" }, now).fetchedAt,
    null,
  );
});

test("an older acquisition cannot replace a newer published snapshot", async () => {
  const s = fixture();
  const newer = { ...feed, fetchedAt: "2026-09-10T18:00:00Z" };
  await publishOdds(newer, s.write, s.read, s.readVersion);
  await assert.rejects(
    publishOdds(feed, s.write, s.read, s.readVersion),
    /older|superseded/i,
  );
  assert.deepEqual(await readStoredOdds(s.read), newer);
});

test("a racing writer cannot replace a newer snapshot after reading an old version", async () => {
  for (const hasInitial of [false, true]) {
    const s = fixture();
    if (hasInitial)
      await publishOdds(
        { ...feed, fetchedAt: "2026-09-10T16:00:00Z" },
        s.write,
        s.read,
        s.readVersion,
      );
    const newer = { ...feed, fetchedAt: "2026-09-10T18:00:00Z" };
    let raced = false;
    const racingWrite: typeof s.write = async (path, body, overwrite, etag) => {
      if (path === "odds/latest.json" && !raced) {
        raced = true;
        await publishOdds(newer, s.write, s.read, s.readVersion);
      }
      await s.write(path, body, overwrite, etag);
    };
    await assert.rejects(
      publishOdds(feed, racingWrite, s.read, s.readVersion),
      /precondition|exists/,
    );
    assert.deepEqual(await readStoredOdds(s.read), newer);
    await assert.rejects(
      publishOdds(feed, s.write, s.read, s.readVersion),
      /superseded/,
    );
    assert.deepEqual(await readStoredOdds(s.read), newer);
  }
});

test("exact retries are idempotent while equal-time conflicting content is rejected", async () => {
  const s = fixture();
  let failAfterCommit = true;
  const write: typeof s.write = async (...args) => {
    await s.write(...args);
    if (args[0] === "odds/latest.json" && failAfterCommit) {
      failAfterCommit = false;
      throw new Error("response lost after commit");
    }
  };
  await assert.rejects(
    publishOdds(feed, write, s.read, s.readVersion),
    /response lost/,
  );
  const priorPointer = s.files.get("odds/latest.json");
  await publishOdds(feed, write, s.read, s.readVersion);
  assert.equal(s.files.get("odds/latest.json"), priorPointer);
  // Equivalent timestamp spelling still denotes the same acquisition instant.
  const conflicting = { ...feed, fetchedAt: "2026-09-10T17:00:00.000Z" };
  await assert.rejects(
    publishOdds(conflicting, s.write, s.read, s.readVersion),
    /Conflicting/,
  );
  assert.deepEqual(await readStoredOdds(s.read), feed);
});
