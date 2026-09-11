import evidence from '../data/weekly-matchup-sources/a8cb653e80978bbbca5dac9aedd37839756b4700c4be09298c40cf0a54e27a16.snapshot.json';
import { test } from "node:test";
import assert from "node:assert/strict";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ExplosiveMatchup } from "../src/components/explosive-matchup";

test("historical matchup compares each offense with the opposing defense and labels samples", () => {
  const html = renderToStaticMarkup(React.createElement(ExplosiveMatchup, {evidence, away: "BUF", home: "NYJ", season: 2026, kickoff: "2026-09-13T17:00:00Z"}));
  assert.match(html, /BUF offense/);
  assert.match(html, /NYJ defense/);
  assert.match(html, /NYJ offense/);
  assert.match(html, /BUF defense/);
  assert.match(html, /2025 regular season and playoffs/);
  assert.match(html, /credited plays/);
  assert.match(html, /20\+ yards/);
  assert.match(html, /10\+ yards/);
  assert.match(html, /Each eligible play counts equally/);
  assert.doesNotMatch(html, /Games count equally/);
});

test("rates use pooled play counts and put each opponent defense in the correct column", () => {
  const html = renderToStaticMarkup(React.createElement(ExplosiveMatchup, {evidence, away: "SF", home: "LA", season: 2026, kickoff: "2026-09-11T00:35:00Z"}));
  const cells = [...html.matchAll(/<strong>([^<]+)<\/strong><small>([^<]+)<\/small>/g)].map(m => [m[1], m[2]]);
  assert.deepEqual(cells, [
    ["8.3%", "55 / 664 credited plays"], ["8.1%", "61 / 755 credited plays"],
    ["9.4%", "48 / 511 credited plays"], ["8.9%", "46 / 517 credited plays"],
    ["11.6%", "86 / 741 credited plays"], ["7.2%", "47 / 655 credited plays"],
    ["11.4%", "59 / 519 credited plays"], ["8.9%", "43 / 482 credited plays"],
  ]);
});

test("historical evidence is withheld for incompatible season, date or teams", () => {
  for (const changes of [{season: 2025}, {season: 2027}, {evidence, away: "constructor"}, {kickoff: null}, {kickoff: "invalid"}, {kickoff: "2026-09-08T00:00:00Z"}]) {
    const html = renderToStaticMarkup(React.createElement(ExplosiveMatchup, {evidence, away: "BUF", home: "NYJ", season: 2026, kickoff: "2026-09-13T17:00:00Z", ...changes}));
    assert.match(html, /Historical comparison unavailable/);
    assert.doesNotMatch(html, /credited plays/);
  }
});
