import { test } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { scheduleSpacing } from "../src/lib/schedule-spacing";
import { ScheduleContext } from "../src/components/schedule-context";
import type { Game } from "../src/lib/types";

const game = {
  id: "next",
  season: 2026,
  week: 3,
  home: "NE",
  away: "SEA",
  kickoff: "2026-09-20T17:00:00Z",
  status: "scheduled",
} as Game;
const prior = {
  ...game,
  id: "prior",
  week: 2,
  kickoff: "2026-09-13T20:00:00Z",
  status: "final",
  actualHome: 20,
  actualAway: 10,
};
const now = Date.parse("2026-09-16T00:00:00Z");
test("spacing uses kickoff instants and does not import an offseason advantage", () => {
  const rows = scheduleSpacing(game, [prior], now);
  assert.equal(rows[0].days, 6.875);
  assert.equal(rows[1].days, 6.875);
  assert.ok(
    scheduleSpacing(game, [{ ...prior, season: 2025 }], now).every(
      (r) => r.days === null,
    ),
  );
  assert.ok(
    scheduleSpacing(game, [prior], Date.parse(prior.kickoff!) + 86400000).every(
      (r) => r.days === null,
    ),
  );
});
test("an intervening unfinished game cannot be silently skipped for an older result", () => {
  const old = { ...prior, id: "old", week: 1, kickoff: "2026-09-06T17:00:00Z" };
  const unfinished = {
    ...prior,
    status: "scheduled",
    actualHome: null,
    actualAway: null,
  };
  assert.ok(
    scheduleSpacing(game, [old, unfinished], now).every(
      (r) => r.days === null && r.reason?.includes("preceding scheduled"),
    ),
  );
  assert.ok(
    scheduleSpacing(game, [old, { ...unfinished, kickoff: null }], now).every(
      (r) => r.days === null,
    ),
  );
  assert.ok(
    scheduleSpacing(game, [prior, prior], now).every((r) => r.days === null),
  );
});
test("equivalent timezone instants cannot select an arbitrary previous game", () => {
  const duplicate = {
    ...prior,
    id: "duplicate",
    kickoff: "2026-09-13T16:00:00-04:00",
  };
  assert.ok(
    scheduleSpacing(game, [prior, duplicate], now).every(
      (r) => r.days === null && r.reason?.includes("ambiguous"),
    ),
  );
});
test("rendered context distinguishes unavailable history and links the underlying game", () => {
  const available = renderToStaticMarkup(
    createElement(ScheduleContext, { game, games: [prior], now }),
  );
  assert.match(available, /6.9 days/);
  assert.match(available, /href="\/games\/prior"/);
  assert.match(available, /does not adjust the model/);
  const missing = renderToStaticMarkup(
    createElement(ScheduleContext, { game, games: [], now }),
  );
  assert.match(missing, /No earlier same-season game/);
  assert.doesNotMatch(missing, /0.0 days/);
});
