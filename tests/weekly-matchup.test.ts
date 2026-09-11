import { test } from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { selectWeeklyContext, type WeeklySnapshot } from '../src/lib/weekly-matchup';
import { WeeklyMatchup } from '../src/components/weekly-matchup';
import { ExplosiveMatchup } from '../src/components/explosive-matchup';
import { RedZoneMatchup } from '../src/components/red-zone-matchup';

const now = Date.now();
const game = { away: 'BUF', home: 'NYJ', season: 2026, week: 2, type: 'REG', kickoff: new Date(now + 3600000).toISOString() };
const side = { gameIds: ['prior-game'], passing: { plays: 20, explosive: 3 }, rushing: { plays: 10, explosive: 1 }, inside20: { possessions: 4, touchdowns: 3 } };
const evidence: WeeklySnapshot = { status: 'ok', season: 2026, week: 2, freshUntil: now + 60000,
  currentSeason: { season: 2026, week: 2, gameType: 'REG', cutoff: '2026-01-01', sourceObservedAt: new Date(now - 60000).toISOString(),
    status: 'available', teams: { BUF: { offense: side, defense: side }, NYJ: { offense: side, defense: side } } } };

test('weekly selection requires exact scope, usable times and both teams', () => {
  assert.ok(selectWeeklyContext(evidence, game, now).data);
  for (const changes of [{week: 1}, {season: 2025}, {type: 'POST'}, {home: 'MIA'}, {home: 'BUF'}, {kickoff: null}])
    assert.equal(selectWeeklyContext(evidence, {...game, ...changes}, now).data, null);
  assert.equal(selectWeeklyContext(evidence, game, evidence.freshUntil!).data, null);
  assert.equal(selectWeeklyContext({...evidence, freshUntil: undefined}, game, now).data, null);
  assert.equal(selectWeeklyContext(evidence, game, now - 120000).data, null);
});

test('weekly rates show pooled counts and separate explicit empty-season state', () => {
  const html = renderToStaticMarkup(React.createElement(WeeklyMatchup, {game, kind: 'big-play', evidence}));
  assert.match(html, /15.0%/);
  assert.match(html, /3 \/ 20 plays/);
  assert.match(html, /Offense sample: 1 game/);
  assert.match(html, /do not change the forecast/);
  const empty = {...evidence, currentSeason: {...evidence.currentSeason!, status: 'no-eligible-games', teams: {}}};
  const emptyHtml = renderToStaticMarkup(React.createElement(WeeklyMatchup, {game, kind: 'inside20', evidence: empty}));
  assert.match(emptyHtml, /No earlier games/);
  assert.doesNotMatch(emptyHtml, /0.0%|<table/);
});

test('no qualifying inside-20 possessions are unavailable, not zero percent', () => {
  const zero = {...side, inside20: {possessions: 0, touchdowns: 0}};
  const sample = {...evidence, currentSeason: {...evidence.currentSeason!, teams: {
    BUF: {offense: zero, defense: side}, NYJ: {offense: side, defense: zero},
  }}};
  const html = renderToStaticMarkup(React.createElement(WeeklyMatchup, {game, kind: 'inside20', evidence: sample}));
  assert.match(html, /Unavailable/);
  assert.match(html, /0 \/ 0 possessions/);
  assert.match(html, /75.0%/);
});

test('missing prior-season evidence cannot suppress the independent current-season panel', () => {
  for (const Component of [ExplosiveMatchup, RedZoneMatchup]) {
    const html = renderToStaticMarkup(React.createElement(Component, {...game, season: 2027}));
    assert.match(html, /This season · 2027/);
    assert.match(html, /Compatible prior-season/);
    assert.doesNotMatch(html, /history remains below/);
  }
});
