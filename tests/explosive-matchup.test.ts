import { test } from "node:test";
import assert from "node:assert/strict";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ExplosiveMatchup } from "../src/components/explosive-matchup";

test("historical matchup compares each offense with the opposing defense and labels samples", () => {
  const html = renderToStaticMarkup(React.createElement(ExplosiveMatchup, {away: "BUF", home: "NYJ", season: 2026, kickoff: "2026-09-13T17:00:00Z"}));
  assert.match(html, /BUF offense/);
  assert.match(html, /NYJ defense/);
  assert.match(html, /NYJ offense/);
  assert.match(html, /BUF defense/);
  assert.match(html, /2025 regular season and playoffs/);
  assert.match(html, /credited plays/);
  assert.match(html, /20\+ yards/);
  assert.match(html, /10\+ yards/);
});

test("historical evidence is withheld for incompatible season, date or teams", () => {
  for (const changes of [{season: 2025}, {season: 2027}, {away: "constructor"}, {kickoff: null}, {kickoff: "invalid"}, {kickoff: "2026-09-08T00:00:00Z"}]) {
    const html = renderToStaticMarkup(React.createElement(ExplosiveMatchup, {away: "BUF", home: "NYJ", season: 2026, kickoff: "2026-09-13T17:00:00Z", ...changes}));
    assert.match(html, /Historical comparison unavailable/);
    assert.doesNotMatch(html, /credited plays/);
  }
});
