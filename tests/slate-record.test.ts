import React from 'react';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { renderToStaticMarkup } from 'react-dom/server';
import { Slate } from '../src/components/slate';
import { site } from '../src/lib/data';

test('completed cards distinguish score-record membership, including ties, from a retained forecast', () => {
  const source = site.games.find(game => game.snapshot)!;
  const render = (graded: boolean, tied = false, status = 'final') => {
    const game = {...source, status, actualHome: 20, actualAway: tied ? 20 : 17};
    return renderToStaticMarkup(React.createElement(Slate, {
      games: [game], gradedGameIds: graded ? [game.id] : [], site,
      initial: {week: game.week, query: '', filter: 'all', sort: 'kickoff'},
      initialNow: Date.parse(site.generatedAt), initialStale: false,
      freshness: [], briefings: {},
      odds: {state: 'not-configured', fetchedAt: '', events: []},
    }));
  };
  assert.match(render(false), /Retained forecast.*Excluded from the live record/);
  assert.doesNotMatch(render(false), /Included in the verified live score record/);
  assert.match(render(true), /Included in the verified live score record/);
  assert.match(render(true, true), /Included in the verified live score record/);
  assert.doesNotMatch(render(false, false, 'scheduled'), /Excluded from the live record|Included in the verified live score record/);
  assert.match(render(false), /Win probabilities exclude ties/);
});
