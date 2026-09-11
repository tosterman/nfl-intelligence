import { test } from "node:test";
import assert from "node:assert/strict";
import { gameReturn } from "../src/lib/game-return";
const game = { home: "PIT", away: "ATL", week: 1 };
test("participating home and away team hubs retain their return path", () => {
  assert.deepEqual(gameReturn('/teams/pit', game), { href: '/teams/pit', label: 'Back to Steelers intelligence' });
  assert.deepEqual(gameReturn('/teams/atl', game), { href: '/teams/atl', label: 'Back to Falcons intelligence' });
});
test("slate query survives unchanged", () => {
  const from = '/?week=1&q=Steelers&filter=forecast&sort=confidence';
  assert.equal(gameReturn(from, game).href, from);
});
test("unrelated teams, external paths and duplicate query values fall back safely", () => {
  for (const from of ['/teams/dal', '/teams/pit/extra', '//example.com', 'https://example.com', '/?week=1\\evil', '/?week=1\n', ['/teams/pit', '/teams/atl'], undefined]) {
    assert.deepEqual(gameReturn(from, game), { href: '/?week=1', label: 'Back to the slate' });
  }
});
