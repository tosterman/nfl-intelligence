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
    write: async (path: string, body: Buffer, overwrite: boolean) => {
      if (files.has(path) && !overwrite) throw new Error("exists");
      files.set(path, body);
    },
  };
};
test("published pointer resolves only to an intact archived snapshot", async () => {
  const s = fixture();
  await publishOdds(feed, s.write, s.read);
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
    ),
  );
  assert.equal(s.files.size, 0);
  let fail = true;
  const write = async (p: string, b: Buffer, o: boolean) => {
    if (p.endsWith("latest.json") && fail) {
      fail = false;
      throw new Error("pointer failed");
    }
    await s.write(p, b, o);
  };
  await assert.rejects(publishOdds(feed, write, s.read));
  assert.equal(await readStoredOdds(s.read), null);
  await publishOdds(feed, write, s.read);
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
  assert.equal(oddsHealth({...feed,state:"unavailable"},now).fetchedAt,null);
});
