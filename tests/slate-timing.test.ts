import { test } from "node:test";
import assert from "node:assert/strict";
import { featuredGame, slateGameStatus } from "../src/lib/slate-timing";
import type { Game } from "../src/lib/types";

const game = (id: string, kickoff: string | null, status = "scheduled") =>
  ({ id, kickoff, status, snapshot: { prediction: {} } }) as Game;

test("spotlight excludes elapsed and invalid kickoffs and chooses earliest future forecast", () => {
  const at = Date.parse("2026-09-11T12:00:00Z");
  const games = [game("past", "2026-09-11T00:35:00Z"), game("later", "2026-09-14T12:00:00Z"),
    game("next", "2026-09-13T12:00:00Z"), game("unknown", null)];
  assert.equal(featuredGame(games, at)?.id, "next");
  assert.equal(featuredGame(games, Date.parse("2026-09-15T00:00:00Z")), undefined);
  assert.equal(featuredGame([game("boundary", new Date(at).toISOString())], at), undefined);
});

test("kickoff closes forecast status without inventing a final score", () => {
  const at = Date.parse("2026-09-11T12:00:00Z");
  const g = game("g", new Date(at).toISOString());
  assert.equal(slateGameStatus(g, at - 1), "Model forecast");
  assert.equal(slateGameStatus(g, at), "Awaiting verified result");
  assert.equal(slateGameStatus({ ...g, status: "final" }, at), "Final");
});
