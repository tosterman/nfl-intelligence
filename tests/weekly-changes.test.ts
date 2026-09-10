import { test } from "node:test";
import assert from "node:assert/strict";
import { weeklyChanges, weeklyBriefing } from "../src/lib/weekly-changes";
import type { Game, Snapshot } from "../src/lib/types";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { WeeklyChanges } from "../src/components/weekly-changes";

const now = Date.parse("2026-09-10T16:00:00Z");
test("server-prepared briefing preserves rendered evidence without shipping histories", () => {
  const ready = fixture("ready");
  const missing = fixture("missing"); missing.snapshot = null;
  const games = [ready, missing];
  const original = structuredClone(games);
  const props = { games, week: 1, asOf: now, returnTo: "/?week=1&q=Rams" };
  const before = renderToStaticMarkup(createElement(WeeklyChanges, props));
  const briefing = weeklyBriefing(games, now);
  const after = renderToStaticMarkup(createElement(WeeklyChanges, { ...props, games: games.map(g => ({ ...g, history: [] })), briefing }));
  assert.equal(after, before);
  assert.deepEqual(games, original);
  assert.ok(!JSON.stringify(briefing).includes('"history"'));
  assert.ok(!JSON.stringify(briefing).includes('"prediction"'));
});
function fixture(id = "g", change = 1): Game {
  const game: Game = { id, season: 2026, week: 1, type: "REG", home: "LA", away: "SF", kickoff: "2026-09-11T00:35:00Z", venue: "Venue", neutral: true, roof: "", status: "scheduled", actualHome: null, actualAway: null, snapshot: null, history: [], market: null, weather: null, injuries: null };
  const { season, week, type, home, away, kickoff, venue, neutral } = game;
  const original: Snapshot = { gameId: id, hash: id + "a", generatedAt: "2026-09-10T14:00:00Z", gameContext: { season, week, type, home, away, kickoff, venue, neutral }, modelVersion: "v1", modelCodeHash: "code", configuration: { weight: 1 }, sourceHash: "schedule", efficiencySourceHashes: ["epa"], trainingGames: 100, trainingThrough: "2026-09-01", prediction: { homeScore: 24, awayScore: 21, homeMargin: 3, total: 45, homeWinProbability: .6, sigmaMargin: 10, sigmaTotal: 10, marginInterval80: [-10, 16], totalInterval80: [30, 60], contributions: [{ name: "Scoring", detail: "Statistical contribution", points: 3 }] } };
  const current = structuredClone(original);
  current.hash = id + "b"; current.generatedAt = "2026-09-10T15:00:00Z";
  current.prediction.homeMargin += change; current.prediction.homeWinProbability += change / 100;
  current.prediction.contributions[0].points += change;
  game.history = [original, current]; game.snapshot = current;
  return game;
}
test("briefing ranks comparable changes and preserves direction and contributing terms", () => {
  const rows = weeklyChanges([fixture("small", 1), fixture("large", -2)], now);
  assert.deepEqual(rows.map((r) => r.game.id), ["large", "small"]);
  assert.equal(rows[0].delta?.margin, -2);
  assert.ok(Math.abs(rows[0].delta!.probabilityPoints + 2) < 1e-10);
  assert.equal(rows[0].contribution?.change, -2);
});
test("first forecasts, model changes and unchanged runs are distinct", () => {
  const first = fixture(); first.history = [first.snapshot!];
  assert.equal(weeklyChanges([first], now)[0].kind, "first");
  const model = fixture(); model.snapshot!.modelCodeHash = "new code";
  const row = weeklyChanges([model], now)[0];
  assert.equal(row.kind, "model"); assert.equal(row.delta, undefined);
  assert.match(weeklyChanges([fixture("same", 0)], now)[0].note, /unchanged/);
});
test("changed context, future or reversed time, incomplete identity and duplicate history suppress comparisons", () => {
  const changes = [
    (g: Game) => { g.venue = "New venue"; },
    (g: Game) => { g.history[0].gameContext = undefined; },
    (g: Game) => { g.snapshot!.generatedAt = "2026-09-11T16:00:00Z"; },
    (g: Game) => { g.history[0].generatedAt = "2026-09-10T15:30:00Z"; },
    (g: Game) => { g.history[0].sourceHash = undefined; },
    (g: Game) => { g.history.push(g.snapshot!); },
    (g: Game) => { g.snapshot!.prediction.homeMargin = NaN; },
  ];
  for (const change of changes) {
    const game = fixture(); change(game); const row = weeklyChanges([game], now)[0];
    assert.equal(row.kind, "unavailable"); assert.equal(row.delta, undefined);
  }
  const empty = fixture(); empty.snapshot = null;
  assert.deepEqual(weeklyChanges([empty], now), []);
});
test("briefing retains links to history even when the active forecast is withheld", () => {
  const game = fixture(); game.snapshot = null;
  const html = renderToStaticMarkup(createElement(WeeklyChanges, { games: [game], week: 1, asOf: now }));
  assert.match(html, /1 matchup history cannot be compared here/);
  assert.match(html, /\/games\/g\?from=%2F%3Fweek%3D1#forecast-changes/);
  assert.doesNotMatch(html, /No retained forecasts/);
});
test("both comparable and unavailable history links retain the selected slate view", () => {
  const returnTo = "/?week=1&q=Rams&filter=forecast&sort=confidence";
  for (const retained of [true, false]) {
    const game = fixture(); if (!retained) game.snapshot = null;
    const html = renderToStaticMarkup(createElement(WeeklyChanges, { games: [game], week: 1, asOf: now, returnTo }));
    assert.ok(html.includes(`?from=${encodeURIComponent(returnTo)}#forecast-changes`));
  }
});
test("briefing displays numerical revision and contribution precision without publication claims", () => {
  const html = renderToStaticMarkup(createElement(WeeklyChanges, { games: [fixture("g", .001)], week: 1, asOf: now }));
  assert.match(html, /Largest reconciled term: Scoring, \+0\.001 points/);
  assert.match(html, /not verified publication/);
  assert.match(html, /percentage points/);
});
