/** Local visual test fixture only; never imported by the application. */
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { writeFileSync } from 'node:fs';
import { WeeklyMatchup } from '../src/components/weekly-matchup';
import type { WeeklySnapshot } from '../src/lib/weekly-matchup';
const now = Date.now();
const game = {season: 2026, week: 5, type: 'REG', away: 'BUF', home: 'NYJ', kickoff: new Date(now + 86400000).toISOString()};
const side = { gameIds: ['one', 'two', 'three', 'four'], passing: {plays: 129, explosive: 11},
  rushing: {plays: 103, explosive: 9}, inside20: {possessions: 13, touchdowns: 8} };
const defense = {...side, passing: {plays: 147, explosive: 17}, inside20: {possessions: 0, touchdowns: 0}};
const opponentDefense = {...side, passing: {plays: 120, explosive: 7}, inside20: {possessions: 6, touchdowns: 2}};
const evidence: WeeklySnapshot = {status: 'ok', season: 2026, week: 5, freshUntil: now + 3600000,
  currentSeason: {season: 2026, week: 5, gameType: 'REG', status: 'available', cutoff: new Date(now - 86400000).toISOString().slice(0, 10),
    sourceObservedAt: new Date(now).toISOString(), teams: {BUF: {offense: side, defense}, NYJ: {offense: defense, defense: opponentDefense}}}};
const html = renderToStaticMarkup(<main style={{maxWidth: 1000, margin: 'auto', padding: 16}}>
  <h1>Weekly matchup layout fixture</h1><p>Synthetic samples for browser testing. These are not NFL results.</p>
  <section className="panel"><h2>Big-play sample</h2><WeeklyMatchup game={game} kind="big-play" evidence={evidence}/></section>
  <section className="panel"><h2>Inside-20 sample</h2><WeeklyMatchup game={game} kind="inside20" evidence={evidence}/></section>
</main>);
writeFileSync('release-recovery/weekly-matchup-fixture.html', html);
