import { test } from "node:test";
import assert from "node:assert/strict";
import { marketDeadlines } from "../src/lib/market-deadlines";
import {
  assessGameOdds,
  ODDS_MAX_AGE_MS,
  type OddsFeed,
} from "../src/lib/odds";

test("market deadlines include each quote expiry and preserve the inclusive age limit", () => {
  const at = Date.parse("2026-09-10T12:00:00Z");
  const game = {
    home: "LA",
    away: "SF",
    kickoff: "2026-09-11T12:00:00Z",
    status: "scheduled",
  };
  const quote = {
    observedAt: new Date(at).toISOString(),
    homePrice: -110,
    awayPrice: -110,
    homePoint: -3,
  };
  const feed: OddsFeed = {
    state: "ready",
    fetchedAt: new Date(at + 1000).toISOString(),
    events: [
      {
        ...game,
        id: "g",
        books: [
          {
            book: "one",
            name: "One",
            spread: quote,
            total: null,
            moneyline: null,
          },
        ],
      },
    ],
  };
  const deadlines = marketDeadlines(feed, game);
  assert.ok(deadlines.includes(at + ODDS_MAX_AGE_MS + 1));
  assert.ok(deadlines.includes(at + 1000 + ODDS_MAX_AGE_MS + 1));
  assert.ok(deadlines.includes(Date.parse(game.kickoff)));
  assert.equal(
    assessGameOdds(feed, game, at + ODDS_MAX_AGE_MS).books.length,
    1,
  );
  assert.equal(
    assessGameOdds(feed, game, at + ODDS_MAX_AGE_MS + 1).books.length,
    0,
  );
  assert.ok(
    !marketDeadlines(feed, { ...game, home: "BUF" }).includes(
      at + ODDS_MAX_AGE_MS + 1,
    ),
  );
  assert.ok(
    marketDeadlines(feed, game, [
      { name: "Model", retrievedAt: quote.observedAt },
    ]).includes(at + 30 * 3600000 + 1),
  );
});
