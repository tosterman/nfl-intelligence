import { test } from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { ModelBrief } from '../src/components/model-brief';
import { site } from '../src/lib/data';

const base = site.games.find(g => g.snapshot)!.snapshot!.prediction;
const render = (points: number[], margin: number) => renderToStaticMarkup(React.createElement(ModelBrief, {
  prediction: {...base, homeMargin: margin, contributions: points.map((value, i) => ({name: `Factor ${i}`, points: value, detail: ''}))}, home: 'Home', away: 'Away',
}));
test('brief preserves an opposing factor even outside the three largest contributions', () => {
  const html = render([4, 3, 2, -1], 8);
  assert.match(html, /Factor 0 adds 4.0 points toward Home/);
  assert.match(html, /Factor 3 adds 1.0 points toward Away/);
  assert.match(html, /href="#model-contributions"/);
  assert.doesNotMatch(html, /Factor 1 adds/);
});
test('brief handles away advantage, no counterweight and invalid accounting', () => {
  assert.match(render([-4, 1], -3), /Factor 0 adds 4.0 points toward Away/);
  assert.doesNotMatch(render([4, 1], 5), /Strongest counterweight/);
  assert.match(render([0], 0), /No single directional advantage/);
  assert.match(render([4], 3), /could not be reconciled/);
  assert.match(render([NaN], 3), /could not be reconciled/);
});
test('all current forecasts have a reconcilable briefing', () => {
  for (const game of site.games.filter(g => g.snapshot)) {
    const html = renderToStaticMarkup(React.createElement(ModelBrief, {prediction: game.snapshot!.prediction, home: game.home, away: game.away}));
    assert.doesNotMatch(html, /could not be reconciled/, game.id);
  }
});
