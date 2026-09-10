import { test } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { MarketCard, MarketPanel } from "../src/components/market-panel";
import type { OddsFeed } from "../src/lib/odds";
import { site } from "../src/lib/data";
const at = "2026-09-10T16:00:00Z";
const game = {
  home: "LA",
  away: "SF",
  status: "scheduled",
  kickoff: "2026-09-11T00:35:00Z",
};
test("slate quote includes price and time and opens with the same spread-bearing sportsbook", () => {
  const pair = { observedAt: at, homePrice: -135, awayPrice: 115 };
  const feed: OddsFeed = {
    state: "ready",
    fetchedAt: at,
    events: [
      {
        id: "g",
        ...game,
        books: [
          {
            book: "fanduel",
            name: "FanDuel",
            spread: null,
            total: null,
            moneyline: pair,
          },
          {
            book: "alpha",
            name: "Alpha",
            spread: { ...pair, homePoint: -3 },
            total: null,
            moneyline: null,
          },
        ],
      },
    ],
  };
  const initialNow = Date.parse(at);
  const card = renderToStaticMarkup(
    createElement(MarketCard, { game, feed, initialNow }),
  );
  assert.match(card, /LAR -3.0 \(-135\)/);
  assert.match(card, /Alpha/);
  assert.match(card, /As of Sep 10/);
  const prediction = site.games.find((g) => g.snapshot)!.snapshot!.prediction;
  const panel = renderToStaticMarkup(
    createElement(MarketPanel, {
      game,
      feed,
      initialNow,
      prediction,
      freshness: [],
    }),
  );
  assert.match(panel, /<option value="alpha" selected="">Alpha<\/option>/);
  const expired = renderToStaticMarkup(
    createElement(MarketCard, {
      game,
      feed,
      initialNow: initialNow + 21600001,
    }),
  );
  assert.doesNotMatch(expired, /-135|As of/);
});
