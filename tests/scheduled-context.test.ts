import { test } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import {
  ScheduledContext,
  ForecastPendingNotice,
} from "../src/components/scheduled-context";
import type { Game } from "../src/lib/types";
const game: Game = {
  id: "future-context-fixture",
  season: 2026,
  week: 2,
  type: "REG",
  home: "CIN",
  away: "TB",
  kickoff: "2026-09-20T17:00:00Z",
  venue: "Unknown fixture venue",
  neutral: false,
  roof: "outdoors",
  status: "scheduled",
  actualHome: null,
  actualAway: null,
  snapshot: null,
  history: [],
  market: null,
  weather: null,
  injuries: null,
};
const now = Date.parse("2026-09-10T12:00:00Z");
test("pending notice never promises a pregame publication after kickoff or with unknown timing", () => {
  const started = renderToStaticMarkup(
    createElement(ForecastPendingNotice, {
      game: { ...game, kickoff: new Date(now).toISOString() },
      now,
    }),
  );
  assert.match(started, /Kickoff has passed/);
  assert.doesNotMatch(started, /will appear|still ahead/);
  const unknown = renderToStaticMarkup(
    createElement(ForecastPendingNotice, {
      game: { ...game, kickoff: null },
      now,
    }),
  );
  assert.match(unknown, /Kickoff timing needs verification/);
  assert.doesNotMatch(unknown, /will appear/);
  const final = renderToStaticMarkup(
    createElement(ForecastPendingNotice, {
      game: { ...game, status: "final" },
      now,
    }),
  );
  assert.match(final, /show the final score/);
  assert.doesNotMatch(final, /still ahead/);
});
test("pending forecasts expose separately checked context and valid fragment links", () => {
  const html = renderToStaticMarkup(
    createElement(ScheduledContext, { game, now }),
  );
  for (const id of ["kickoff-weather", "personnel-reports"]) {
    assert.ok(html.includes(`href="#${id}"`));
    assert.ok(html.includes(`id="${id}"`));
  }
  assert.match(html, /Verified venue forecast unavailable/);
  assert.match(html, /not a promised starter/);
  assert.doesNotMatch(html, /Model versus market|fair moneyline/);
});
test("completed, started and unknown-kickoff games do not expose pending-game context", () => {
  for (const g of [
    { ...game, status: "final" },
    { ...game, kickoff: null },
    { ...game, kickoff: "invalid" },
    { ...game, kickoff: new Date(now).toISOString() },
  ])
    assert.equal(
      renderToStaticMarkup(createElement(ScheduledContext, { game: g, now })),
      "",
    );
});
