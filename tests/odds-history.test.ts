import { test } from "node:test";
import assert from "node:assert/strict";
import { historyForGame, selectRecentArchives } from "../src/lib/odds-history";
import type { OddsFeed } from "../src/lib/odds";
test("archive cap cannot hide one member of a conflicting timestamp group", () => {
  const path = (minute: number, hash: string) =>
    `odds/2026-09-10/2026-09-10T17-${String(minute).padStart(2, "0")}-00.000Z-${hash.repeat(64)}.json.gz`;
  const input = [
    path(0, "a"),
    path(0, "b"),
    ...Array.from({ length: 11 }, (_, i) => path(i + 1, "c")),
  ];
  const result = selectRecentArchives(input);
  assert.equal(result.paths.length, 11);
  assert.equal(result.conflicts, 1);
  assert.ok(
    !result.paths.includes(input[0]) && !result.paths.includes(input[1]),
  );
});
const game = {
  home: "LA",
  away: "SF",
  kickoff: "2026-09-11T00:35:00Z",
  status: "final",
};
const feed = (at: string): OddsFeed => ({
  state: "ready",
  fetchedAt: at,
  events: [
    {
      id: "one",
      home: "LA",
      away: "SF",
      kickoff: game.kickoff,
      books: [
        {
          book: "fanduel",
          name: "FanDuel",
          spread: {
            observedAt: at,
            homePrice: -110,
            awayPrice: -110,
            homePoint: -3.5,
          },
          total: null,
          moneyline: null,
        },
      ],
    },
  ],
});
test("history keeps eligible pregame observations after kickoff and orders acquisition times", () => {
  const a = feed("2026-09-10T17:00:00Z"),
    b = feed("2026-09-10T21:00:00Z");
  assert.deepEqual(
    historyForGame([b, a, a], game, Date.parse("2026-09-11T02:00:00Z")).map(
      (r) => r.fetchedAt,
    ),
    [a.fetchedAt, b.fetchedAt],
  );
});
test("history rejects post-kickoff, future, stale-market and rescheduled observations", () => {
  const stale = feed("2026-09-10T17:00:00Z");
  stale.events[0].books[0].spread!.observedAt = "2026-09-10T10:00:00Z";
  const moved = feed("2026-09-10T17:01:00Z");
  moved.events[0].kickoff = "2026-09-11T00:36:00Z";
  assert.equal(
    historyForGame(
      [
        stale,
        moved,
        feed("2026-09-11T01:00:00Z"),
        feed("2026-09-10T23:00:00Z"),
      ],
      game,
      Date.parse("2026-09-10T22:00:00Z"),
    ).length,
    0,
  );
});
test("conflicting captures with the same acquisition time are withheld", () => {
  const a = feed("2026-09-10T17:00:00Z"),
    b = structuredClone(a);
  b.events[0].books[0].spread!.homePoint = -4;
  assert.equal(
    historyForGame([a, b], game, Date.parse("2026-09-10T22:00:00Z")).length,
    0,
  );
});
