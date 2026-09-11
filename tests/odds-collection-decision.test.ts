import { test } from "node:test";
import assert from "node:assert/strict";
import { decideCollection } from "../src/lib/odds-collection-decision";

const now = Date.parse("2026-09-13T16:50:00Z");
const base = {
  now,
  history: { complete: true, observedAt: now, attempts: [] as number[] },
  feed: null,
  games: [{ home: "DET", away: "NO", kickoff: "2026-09-13T17:00:00Z" }],
};
test("missing or incomplete history never becomes an empty budget", () => {
  assert.equal(
    decideCollection({ ...base, history: null }).reason,
    "history-unavailable",
  );
  assert.equal(
    decideCollection({ ...base, history: { ...base.history, complete: false } })
      .reason,
    "history-unavailable",
  );
});
test("closing capture is due at ten minutes before kickoff, never at kickoff", () => {
  assert.equal(decideCollection(base).reason, "closing-window");
  assert.equal(
    decideCollection({
      ...base,
      now: now + 600000,
      history: { ...base.history, observedAt: now + 600000 },
    }).reason,
    "regular-refresh",
  );
});
test("cooldown and rolling cap still block a due closing request", () => {
  assert.equal(
    decideCollection({
      ...base,
      history: { ...base.history, attempts: [now - 60000] },
    }).reason,
    "cooldown",
  );
  const attempts = Array.from(
    { length: 155 },
    (_, i) => now - (156 - i) * 3600000,
  );
  assert.equal(
    decideCollection({ ...base, history: { ...base.history, attempts } })
      .reason,
    "budget-exhausted",
  );
});
test("a recent capture of another event cannot satisfy this game", () => {
  const feed = {
    state: "ready" as const,
    fetchedAt: new Date(now - 60000).toISOString(),
    events: [
      {
        id: "x",
        home: "CHI",
        away: "GB",
        kickoff: base.games[0].kickoff,
        books: [],
      },
    ],
  };
  assert.equal(decideCollection({ ...base, feed }).reason, "closing-window");
  assert.equal(
    decideCollection({
      ...base,
      feed: { ...feed, events: [{ ...feed.events[0], ...base.games[0] }] },
    }).reason,
    "recent-capture",
  );
});
test("future or stale history and duplicate attempts are rejected", () => {
  for (const history of [
    { ...base.history, observedAt: now + 1 },
    { ...base.history, observedAt: now - 60001 },
    { ...base.history, attempts: [now - 1, now - 1] },
    { ...base.history, observedAt: now - 1000, attempts: [now - 500] },
  ])
    assert.equal(
      decideCollection({ ...base, history }).reason,
      "invalid-history",
    );
});
