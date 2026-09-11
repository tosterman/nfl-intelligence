import { test } from "node:test";
import assert from "node:assert/strict";
import { runPlannedOddsCollection } from "../src/lib/planned-odds-collector";
import { normalizeOdds, type OddsFeed } from "../src/lib/odds";
import { prepareArchive } from "../src/lib/odds-archive";

function fixture() {
  const now = Date.parse("2026-09-13T16:50:00Z");
  let saved: OddsFeed | null = normalizeOdds([], new Date(now - 60000).toISOString());
  const attempts: number[] = [];
  const calls = { paid: 0, quota: 0 };
  const options = {
    games: [{ home: "DET", away: "NO", kickoff: "2026-09-13T17:00:00Z" }],
    readHistory: async () => ({ complete: true, observedAt: now, attempts: [...attempts] }),
    collector: {
      key: "fixture", now: () => now, read: async () => saved,
      reserve: async (at: number) => {
        if (attempts.length) throw new Error("atomic reservation denied");
        attempts.push(at); return at + 1800000;
      },
      publish: async (feed: OddsFeed) => { saved = feed; return { fetchedAt: feed.fetchedAt, sha256: prepareArchive(feed).sha256, events: feed.events.length }; },
      fetcher: (async (url) => {
        if (new URL(String(url)).pathname === "/v4/sports/") calls.quota++;
        else calls.paid++;
        return Response.json([], { headers: { "x-requests-remaining": "30" } });
      }) as typeof fetch,
    },
  };
  return { options, calls, attempts };
}

test("incomplete history prevents even a quota lookup", async () => {
  const { options, calls } = fixture();
  options.readHistory = async () => ({ complete: false, observedAt: options.collector.now(), attempts: [] });
  const result = await runPlannedOddsCollection(options);
  assert.equal(result.status, "deferred");
  assert.deepEqual(calls, { paid: 0, quota: 0 });
});

test("due exact-event collection is not overridden by general snapshot reuse", async () => {
  const { options, calls, attempts } = fixture();
  assert.equal((await runPlannedOddsCollection(options)).status, "captured");
  assert.equal(calls.paid, 1);
  assert.equal(attempts.length, 1);
  assert.equal((await runPlannedOddsCollection(options)).status, "deferred");
  assert.equal(calls.paid, 1);
});

test("history is rechecked after quota lookup and before reservation", async () => {
  const { options, calls, attempts } = fixture();
  let reads = 0;
  options.readHistory = async () => ({ complete: ++reads === 1, observedAt: options.collector.now(), attempts: [] });
  assert.equal((await runPlannedOddsCollection(options)).status, "deferred");
  assert.deepEqual(calls, { paid: 0, quota: 1 });
  assert.equal(attempts.length, 0);
});

test("concurrent planned collectors cannot bypass the atomic reservation", async () => {
  const { options, calls, attempts } = fixture();
  const outcomes = await Promise.allSettled([runPlannedOddsCollection(options), runPlannedOddsCollection(options)]);
  assert.equal(outcomes.filter(r => r.status === "fulfilled" && r.value.status === "captured").length, 1);
  for (const outcome of outcomes) {
    if (outcome.status === "rejected") assert.match(String(outcome.reason), /atomic reservation denied/);
  }
  assert.equal(calls.paid, 1);
  assert.equal(attempts.length, 1);
});

test("provider timeout retains the attempt and prevents an immediate retry", async () => {
  const { options, calls, attempts } = fixture();
  const fetcher = options.collector.fetcher;
  options.collector.fetcher = (async (url, init) => {
    if (new URL(String(url)).pathname === "/v4/sports/") return fetcher(url, init);
    calls.paid++;
    throw new Error("provider timeout");
  }) as typeof fetch;
  await assert.rejects(runPlannedOddsCollection(options), /provider timeout/);
  assert.equal(attempts.length, 1);
  assert.equal((await runPlannedOddsCollection(options)).status, "deferred");
  assert.equal(calls.paid, 1);
});

test("a closing-only request is withheld if reservation completes at kickoff", async () => {
  const { options, calls, attempts } = fixture();
  const kickoff = Date.parse(options.games[0].kickoff);
  let at = kickoff - 1;
  options.collector.now = () => at;
  options.readHistory = async () => ({ complete: true, observedAt: at, attempts: [...attempts] });
  const reserve = options.collector.reserve;
  options.collector.reserve = async (time) => { const expiry = await reserve(time); at = kickoff; return expiry; };
  assert.equal((await runPlannedOddsCollection(options)).status, "deferred");
  assert.equal(calls.paid, 0);
  assert.equal(attempts.length, 1, "the reservation is retained even when the window closes");
});

test("reservation mutation of a reader-owned history array cannot self-block", async () => {
  const { options, calls, attempts } = fixture();
  options.readHistory = async () => ({ complete: true, observedAt: options.collector.now(), attempts });
  assert.equal((await runPlannedOddsCollection(options)).status, "captured");
  assert.equal(calls.paid, 1);
});
