import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { LiveRecordSummary } from '../src/components/live-record-summary';

const render = (games: number, wins: number, ties: number, missed: number) =>
  renderToStaticMarkup(createElement(LiveRecordSummary, { record: { games, wins, ties, missed } }));

test('empty live record reports missing coverage without fabricated accuracy', () => {
  const html = render(0, 0, 0, 2);
  assert.match(html, /No eligible decisive results yet/);
  assert.match(html, /2 completed games excluded/);
  assert.doesNotMatch(html, /NaN|0%|63/);
  assert.match(html, /All tracked games/);
});

test('tied-only sample remains separate from decisive accuracy', () => {
  const html = render(0, 0, 2, 0);
  assert.match(html, /No eligible decisive results yet/);
  assert.match(html, /2 eligible ties/);
  assert.match(html, /excluded from winner accuracy/);
});

test('populated summary uses only eligible decisive results and shows exclusions', () => {
  const html = render(10, 6, 1, 3);
  assert.match(html, /6 of 10 decisive games correct/);
  assert.match(html, /1 eligible tie /);
  assert.match(html, /3 completed games excluded/);
  assert.match(html, /verified pregame publication/);
  assert.match(html, /href="\/performance"/);
});
