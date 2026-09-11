import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { writeFileSync } from 'node:fs';
import { Slate } from '../src/components/slate';
import { site } from '../src/lib/data';

const at = '2026-09-11T12:00:00Z';
const source = site.games.find(g => g.snapshot)!;
const game = {...source, status: 'scheduled' as const, kickoff: '2026-09-12T12:00:00Z',
  snapshot: {...source.snapshot!, prediction: {...source.snapshot!.prediction, homeScore: 26.25, awayScore: 20.75, homeMargin: 5.5, total: 47}}};
const feed = {state: 'ready' as const, fetchedAt: at, events: [{id: 'synthetic', home: game.home, away: game.away,
  kickoff: game.kickoff, books: [{book: 'fanduel', name: 'Synthetic Sportsbook', moneyline: null,
    spread: {observedAt: at, homePoint: -3.5, homePrice: -110, awayPrice: -110},
    total: {observedAt: at, point: 45, overPrice: -105, underPrice: -115}}]}]};
const html = renderToStaticMarkup(<main><h1>Synthetic market layout test</h1><Slate games={[game]}
  site={site} gradedGameIds={[]} initial={{week: game.week, query: '', filter: 'all', sort: 'kickoff'}}
  freshness={[{name: 'fixture', retrievedAt: at}]} initialStale={false}
  odds={feed} initialNow={Date.parse(at)} briefings={{}} /></main>);
writeFileSync('release-recovery/slate-market-fixture.html', html);
