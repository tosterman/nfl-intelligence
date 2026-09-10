import { test } from "node:test";
import assert from "node:assert/strict";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import { prepareArchive, archiveOdds } from "../src/lib/odds-archive";
import type { OddsFeed } from "../src/lib/odds";
const feed: OddsFeed = {
  state: "ready",
  fetchedAt: "2026-09-10T17:00:00Z",
  events: [],
};
test("archive has verifiable contents and bounded deterministic path", () => {
  const a = prepareArchive(feed),
    b = prepareArchive(structuredClone(feed));
  assert.equal(a.pathname, b.pathname);
  const content = gunzipSync(a.body);
  assert.equal(createHash("sha256").update(content).digest("hex"), a.sha256);
  assert.deepEqual(JSON.parse(content.toString()).feed, feed);
  assert.match(
    a.pathname,
    /^odds\/2026-09-10\/[A-Za-z0-9T.-]+-[a-f0-9]{64}\.json\.gz$/,
  );
  assert.throws(() => prepareArchive({ ...feed, state: "unavailable" }));
  assert.throws(() => prepareArchive({ ...feed, fetchedAt: "bad" }));
});
test("writer enforces private non-overwriting storage and propagates failure", async () => {
  let calls = 0;
  const write = async (
    path: string,
    body: Buffer,
    options: Record<string, unknown>,
  ) => {
    calls++;
    assert.equal(options.access, "private");
    assert.equal(options.allowOverwrite, false);
    assert.equal(options.addRandomSuffix, false);
    assert.ok(body.length);
    return { pathname: path };
  };
  const result = await archiveOdds(feed, write);
  assert.equal(calls, 1);
  assert.ok(result.sha256);
  await assert.rejects(
    archiveOdds(feed, async () => {
      throw new Error("storage offline");
    }),
  );
});
