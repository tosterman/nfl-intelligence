import { test } from "node:test";
import assert from "node:assert/strict";
import {
  authorizedCollector,
  canReuseSnapshot,
  runOddsCollection,
} from "../src/lib/odds-collector";
import { prepareArchive } from "../src/lib/odds-archive";
import { reserveOddsAcquisition } from "../src/lib/odds-store";
import type { OddsFeed } from "../src/lib/odds";

function collectorFixture() {
  const at = Date.parse("2026-09-10T16:00:00Z");
  let saved: OddsFeed | null = null;
  const calls = { fetch: 0, publish: 0, read: 0 };
  const deps = {
    key: "test-key",
    now: () => at,
    reserve: async (now: number) => now + 30 * 60 * 1000,
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
    fetcher: (async (url) => {
      if (new URL(String(url)).pathname === "/v4/sports/")
        return Response.json([], { headers: { "x-requests-remaining": "12" } });
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
  const originalFetch = failed.deps.fetcher;
  failed.deps.fetcher = (async (url, options) => {
    if (new URL(String(url)).pathname === "/v4/sports/")
      return originalFetch(url, options);
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
test("unknown or insufficient quota blocks paid acquisition", async () => {
  for (const remaining of [
    null,
    "",
    "2",
    "0",
    "-1",
    "3.5",
    "3x",
    "9007199254740992",
  ]) {
    const { deps, calls } = collectorFixture();
    const original = deps.fetcher;
    deps.fetcher = (async (url, options) => {
      if (new URL(String(url)).pathname !== "/v4/sports/")
        return original(url, options);
      return Response.json([], {
        headers:
          remaining === null ? {} : { "x-requests-remaining": remaining },
      });
    }) as typeof fetch;
    await assert.rejects(runOddsCollection(deps), /quota/);
    assert.equal(calls.fetch, 0);
    assert.equal(calls.publish, 0);
  }
});
test("quota check is free, precedes acquisition, and is skipped for fresh storage", async () => {
  const { deps, calls } = collectorFixture();
  const original = deps.fetcher;
  const paths: string[] = [];
  deps.fetcher = (async (url, options) => {
    paths.push(new URL(String(url)).pathname);
    if (paths.at(-1) === "/v4/sports/")
      return Response.json([], { headers: { "x-requests-remaining": "3" } });
    return original(url, options);
  }) as typeof fetch;
  await runOddsCollection(deps);
  await runOddsCollection(deps);
  assert.deepEqual(paths, [
    "/v4/sports/",
    "/v4/sports/americanfootball_nfl/odds/",
  ]);
  assert.equal(calls.fetch, 1);
  const failed = collectorFixture();
  failed.deps.fetcher = (async () =>
    new Response(null, { status: 503 })) as typeof fetch;
  await assert.rejects(runOddsCollection(failed.deps), /quota/);
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

test("a denied acquisition reservation prevents a paid request", async () => {
  const { deps, calls } = collectorFixture();
  await assert.rejects(
    runOddsCollection({
      ...deps,
      reserve: async () => {
        throw new Error("Odds acquisition already reserved");
      },
    }),
    /reserved/,
  );
  assert.equal(calls.fetch, 0);
});

test("an expired reservation cannot authorize a delayed paid request", async () => {
  const { deps, calls } = collectorFixture();
  deps.reserve = async (at) => {
    deps.now = () => at + 30 * 60 * 1000;
    return at + 30 * 60 * 1000;
  };
  // Pass a stable function that sees the updated simulated clock.
  await assert.rejects(
    runOddsCollection({ ...deps, now: () => deps.now() }),
    /reservation expired/,
  );
  assert.equal(calls.fetch, 0);
});

test("overlapping collectors and a retry after provider timeout spend at most one request", async () => {
  for (const providerFails of [false, true]) {
    const { deps, calls } = collectorFixture();
    let reservation: { body: Buffer; etag: string } | null = null;
    let version = 0;
    deps.reserve = (at) =>
      reserveOddsAcquisition(
        at,
        async () => reservation,
        async (_path, body, overwrite, ifMatch) => {
          if (reservation && (!overwrite || ifMatch !== reservation.etag))
            throw new Error("reservation conflict");
          reservation = { body, etag: String(++version) };
        },
      );
    if (providerFails) {
      const fetcher = deps.fetcher;
      deps.fetcher = (async (url, options) => {
        if (new URL(String(url)).pathname === "/v4/sports/")
          return fetcher(url, options);
        calls.fetch++;
        throw new Error("provider timeout after possible charge");
      }) as typeof fetch;
    }
    const outcomes = await Promise.allSettled(
      Array.from({ length: 8 }, () => runOddsCollection(deps)),
    );
    assert.equal(calls.fetch, 1);
    assert.equal(
      outcomes.filter((r) => r.status === "fulfilled").length,
      providerFails ? 0 : 1,
    );
    if (providerFails)
      await assert.rejects(runOddsCollection(deps), /reserved/);
    else
      assert.equal((await runOddsCollection(deps)).status, "already-current");
    assert.equal(calls.fetch, 1);
  }
});
