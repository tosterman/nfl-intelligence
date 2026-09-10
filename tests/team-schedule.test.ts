import { test } from "node:test";
import assert from "node:assert/strict";
import { nextScheduledGame } from "../src/lib/team-schedule";
import type { Game } from "../src/lib/types";

const game = (id: string, week: number, status = "scheduled"): Game => ({
  id, week, status, season: 2026, type: "REG", home: "NE", away: "NYJ",
  kickoff: null, venue: "Test venue", neutral: false, roof: "",
  actualHome: null, actualAway: null, snapshot: null, history: [], market: null,
  weather: null, injuries: null,
});
test("next matchup remains visible without a forecast or announced kickoff time", () => {
  const later = game("later", 3), next = game("next", 2), final = game("final", 1, "final");
  const input = [later, final, next];
  assert.equal(nextScheduledGame(input, "NE"), next);
  assert.deepEqual(input, [later, final, next]);
  assert.equal(nextScheduledGame(input, "DAL"), undefined);
  assert.equal(nextScheduledGame([final, game("live", 2, "in-progress")], "NE"), undefined);
});
