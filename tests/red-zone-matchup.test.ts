import { test } from "node:test";
import assert from "node:assert/strict";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { RedZoneMatchup } from "../src/components/red-zone-matchup";

test("red-zone comparison labels historical possessions and the strict boundary", () => {
  const html = renderToStaticMarkup(React.createElement(RedZoneMatchup, {away: "SF", home: "LA", season: 2026, kickoff: "2026-09-11T00:35:00Z"}));
  assert.match(html, /SF offense/);
  assert.match(html, /LA defense/);
  assert.match(html, /strictly inside/);
  assert.match(html, /2025 regular season and playoffs/);
  assert.match(html, /touchdowns from/);
  assert.match(html, /do not change the forecast/);
});

test("red-zone evidence is unavailable for missing dates and incompatible seasons", () => {
  for (const changes of [{season: 2025}, {season: 2027}, {away: "constructor"}, {kickoff: null}, {kickoff: "bad"}]) {
    const html = renderToStaticMarkup(React.createElement(RedZoneMatchup, {away: "SF", home: "LA", season: 2026, kickoff: "2026-09-11T00:35:00Z", ...changes}));
    assert.match(html, /Inside-20 history unavailable/);
    assert.doesNotMatch(html, /touchdowns from/);
  }
});
