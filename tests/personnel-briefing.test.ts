import { test } from 'node:test';
import assert from 'node:assert/strict';
import { groupPersonnel } from '../src/lib/personnel-briefing';
import type { PlayerReport } from '../src/lib/personnel';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { PersonnelBriefing, ParticipationFactView } from '../src/components/personnel-briefing';

test('briefing preserves every report without turning practice into availability', () => {
  const statuses = [null, 'Questionable', 'Out', 'Doubtful', 'Other'];
  const players = statuses.map((reportStatus, i) => ({playerId:String(i), reportStatus, practiceStatus:'Did Not Participate'} as PlayerReport));
  const groups = groupPersonnel(players);
  assert.deepEqual(groups.map(g=>g.label), ['Reported out', 'Reported doubtful', 'Reported questionable', 'Other game designations', 'No game designation']);
  assert.deepEqual(groups.flatMap(g=>g.players).map(p=>p.playerId).sort(), players.map(p=>p.playerId).sort());
  assert.equal(groups.at(-1)!.players[0].reportStatus, null);
  assert.equal(groupPersonnel([]).length, 0);
});

test('rendered briefing keeps unavailable identity evidence visible for every designation', () => {
  const players = ['Out', 'Doubtful', 'Questionable', null].map((reportStatus, i) => ({
    playerId:String(i), name:`Report ${i}`, position:'CB', team:'PIT', season:2026, type:'REG', week:1,
    reportStatus, practiceStatus:'Did Not Participate', reportInjury:null, practiceInjury:null, practiceSecondaryInjury:null,
  }));
  const snapshot = {status:'available', sourceHash:'a'.repeat(64), retrievedAt:'2026-09-11T00:00:00Z', assetUpdatedAt:'2026-09-11T00:00:00Z', players};
  const html = renderToStaticMarkup(createElement(PersonnelBriefing,{snapshot,players,current:null,historical:null}));
  for (const player of players) assert.ok(html.includes(player.name));
  for (const label of ['Reported out', 'Reported doubtful', 'Reported questionable', 'Game availability is unreported', 'Missing history does not mean zero']) assert.ok(html.includes(label), label);
  assert.equal((html.match(/earlier-week participation is not verified/g) ?? []).length, 4);
});

test('valid current-season evidence survives a historical identity conflict', () => {
  const season = {season:2026, sourceRetrievedAt:'2026-09-16T00:00:00Z', retained:false, cutoff:'2026-09-16T00:00:00Z',
    appearances:1, shares:{offense:.5, defense:0, specialTeams:.1}, lastAppearance:'2026-09-10T00:00:00Z', currentTeamAppearances:1, formerTeamAppearances:0};
  const html = renderToStaticMarkup(createElement(ParticipationFactView,{season,prior:null,historicalConflict:true,sharedEmpty:false,year:2026}));
  assert.ok(html.includes('2026 earlier weeks: offense 50%'));
  assert.ok(html.includes('Prior-season identity unresolved'));
  assert.ok(!html.includes('Identity unresolved · participation withheld'));
});
