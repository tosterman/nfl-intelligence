import { test } from "node:test";
import assert from "node:assert/strict";
import {
  authorizedCollector,
  canReuseSnapshot,
  runOddsCollection,
} from "../src/lib/odds-collector";
import { prepareArchive } from "../src/lib/odds-archive";
import type { OddsFeed } from "../src/lib/odds";

function collectorFixture() {
  const at = Date.parse("2026-09-10T16:00:00Z");
  let saved: OddsFeed | null = null;
  const calls = { fetch: 0, publish: 0, read: 0 };
  const deps = {
    key: "test-key",
    now: () => at,
    read: async () => {
      calls.read++;
      return saved;
    },
    publish: async (feed: OddsFeed) => {
      calls.publish++;
      saved = feed;
      return {
        fetchedAt: feed.fetchedAt,
        sha256: prepareArchive(feed).sha256,
        events: feed.events.length,
      };
    },
    fetcher: (async () => {
      calls.fetch++;
      return Response.json([], { headers: { "x-requests-remaining": "12" } });
    }) as typeof fetch,
  };
  return { deps, calls };
}
test("storage retry uses one provider response and verifies exact readback", async () => {
  const { deps, calls } = collectorFixture();
  const publish = deps.publish;
  let attempts = 0;
  deps.publish = async (feed) => {
    attempts++;
    if (attempts < 3) throw new Error("storage timeout");
    return publish(feed);
  };
  const result = await runOddsCollection(deps);
  assert.equal(result.status, "captured");
  assert.equal(attempts, 3);
  assert.equal(calls.fetch, 1);
  await runOddsCollection(deps);
  assert.equal(
    calls.fetch,
    1,
    "fresh stored response must prevent another acquisition",
  );
});
test("persistent storage failure and rejected provider response do not reacquire", async () => {
  const { deps, calls } = collectorFixture();
  let attempts = 0;
  deps.publish = async () => {
    attempts++;
    throw new Error("storage timeout");
  };
  await assert.rejects(runOddsCollection(deps), /Odds storage failed/);
  assert.equal(attempts, 3);
  assert.equal(calls.fetch, 1);
  const failed = collectorFixture();
  failed.deps.fetcher = (async () => {
    failed.calls.fetch++;
    return new Response("quota exceeded", { status: 429 });
  }) as typeof fetch;
  await assert.rejects(
    runOddsCollection(failed.deps),
    /Odds acquisition failed/,
  );
  assert.equal(failed.calls.fetch, 1);
  assert.equal(failed.calls.publish, 0);
});
test("unreadable storage prevents acquisition and wrong readback cannot report success", async () => {
  const { deps, calls } = collectorFixture();
  deps.read = async () => {
    throw new Error("storage unavailable");
  };
  await assert.rejects(runOddsCollection(deps));
  assert.equal(calls.fetch, 0);
  const mismatch = collectorFixture();
  let reads = 0;
  mismatch.deps.read = async () =>
    ++reads === 1
      ? null
      : { state: "ready", fetchedAt: "2026-09-10T15:59:00Z", events: [] };
  await assert.rejects(
    runOddsCollection(mismatch.deps),
    /Odds readback failed/,
  );
  assert.equal(mismatch.calls.fetch, 1);
});
test("collection requires a configured long secret and exact bearer credential", () => {
  const secret = "a".repeat(64);
  assert.equal(authorizedCollector(null, secret), false);
  assert.equal(authorizedCollector("Bearer " + secret, undefined), false);
  assert.equal(authorizedCollector("Bearer " + secret, secret), true);
  assert.equal(authorizedCollector("Bearer " + secret + "x", secret), false);
  assert.equal(authorizedCollector("Bearer weak", "weak"), false);
});
test("manual collection cannot suppress a scheduled capture for hours", () => {
  const feed = {
    state: "ready" as const,
    fetchedAt: "2026-09-10T14:17:00Z",
    events: [],
  };
  const fetched = Date.parse(feed.fetchedAt);
  assert.equal(canReuseSnapshot(feed, fetched + 29 * 60000), true);
  assert.equal(canReuseSnapshot(feed, fetched + 30 * 60000), false);
  assert.equal(canReuseSnapshot(feed, fetched + 2 * 3600000), false);
});
