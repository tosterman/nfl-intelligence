import { test } from "node:test";
import assert from "node:assert/strict";
import { normalizeOdds, quotesForGame } from "../src/lib/odds";
const at = "2026-09-10T16:00:00Z";
const game = {
  home: "LA",
  away: "SF",
  kickoff: "2026-09-11T00:35:00Z",
  status: "scheduled",
};
function event() {
  return {
    id: "abc",
    sport_key: "americanfootball_nfl",
    home_team: "Los Angeles Rams",
    away_team: "San Francisco 49ers",
    commence_time: game.kickoff,
    bookmakers: [
      {
        key: "fanduel",
        title: "FanDuel",
        last_update: at,
        markets: [
          {
            key: "spreads",
            last_update: at,
            outcomes: [
              { name: "Los Angeles Rams", point: -3, price: -110 },
              { name: "San Francisco 49ers", point: 3, price: -110 },
            ],
          },
          {
            key: "h2h",
            last_update: at,
            outcomes: [
              { name: "Los Angeles Rams", price: -150 },
              { name: "San Francisco 49ers", price: 130 },
            ],
          },
        ],
      },
    ],
  };
}
test("real schema maps identity and complete opposing outcomes", () => {
  const feed = normalizeOdds([event()], at);
  const q = quotesForGame(feed, game, Date.parse(at));
  assert.equal(q.length, 1);
  assert.equal(q[0].spread?.homePoint, -3);
  assert.equal(q[0].moneyline?.awayPrice, 130);
  assert.equal(q[0].total, null);
  assert.deepEqual(
    quotesForGame(feed, { ...game, home: "SF", away: "LA" }, Date.parse(at)),
    [],
  );
  assert.deepEqual(
    quotesForGame(
      feed,
      { ...game, kickoff: "2026-09-12T00:35:00Z" },
      Date.parse(at),
    ),
    [],
  );
});
test("stale, future and started quotes are withheld", () => {
  const feed = normalizeOdds([event()], at);
  for (const now of [
    Date.parse(at) - 1,
    Date.parse(at) + 21600001,
    Date.parse(game.kickoff),
  ])
    assert.equal(quotesForGame(feed, game, now).length, 0);
  assert.equal(
    quotesForGame(feed, { ...game, status: "final" }, Date.parse(at)).length,
    0,
  );
});
test("malformed pair does not erase other valid market", () => {
  const e = event();
  (e.bookmakers[0].markets[0].outcomes[1] as { point: number }).point = 4;
  const q = quotesForGame(normalizeOdds([e], at), game, Date.parse(at));
  assert.equal(q[0].spread, null);
  assert.ok(q[0].moneyline);
  e.bookmakers[0].markets[1].outcomes[0].price = 0;
  assert.equal(
    quotesForGame(normalizeOdds([e], at), game, Date.parse(at)).length,
    0,
  );
});
test("invalid payload and duplicate events fail closed", () => {
  assert.throws(() => normalizeOdds({ message: "error" }, at));
  assert.throws(() => normalizeOdds([event(), event()], at));
  assert.throws(() => normalizeOdds([], "invalid"));
});

test("kickoff mismatch and duplicate bookmaker identity are withheld", () => {
  const e = event();
  e.commence_time = "2026-09-11T00:30:00Z";
  assert.equal(
    quotesForGame(normalizeOdds([e], at), game, Date.parse(at)).length,
    0,
  );
  const duplicate = event();
  duplicate.bookmakers.push(structuredClone(duplicate.bookmakers[0]));
  assert.equal(
    quotesForGame(normalizeOdds([duplicate], at), game, Date.parse(at)).length,
    0,
  );
});
