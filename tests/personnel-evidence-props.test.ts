import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { PersonnelBriefing } from '../src/components/personnel-briefing';
import { PlayerUsage } from '../src/components/player-usage';
import { PersonnelPanel } from '../src/components/personnel-panel';
import type { Game } from '../src/lib/types';
import { staticPersonnelEvidence } from '../src/lib/personnel-static';

test('missing runtime publication keeps report availability unknown', () => {
  const html=renderToStaticMarkup(createElement(PersonnelPanel,{game:{} as Game,evidence:null}));
  assert.match(html,/Verified player reports are unavailable/);
  assert.match(html,/Availability is unknown/);
  assert.doesNotMatch(html,/Full reports|Listed first|File updated/);
});

function fixture() {
  const acquired = new Date(Date.now() - 60000).toISOString();
  const player = {playerId:'00-1234567', name:'Injected player', team:'PIT', season:2026,
    type:'REG', week:1, position:'WR', reportStatus:'Questionable', practiceStatus:null,
    reportInjury:null, practiceInjury:null, practiceSecondaryInjury:null};
  const snapshot = {status:'available', sourceHash:'a'.repeat(64), retrievedAt:acquired,
    assetUpdatedAt:acquired, players:[player]};
  const current = {schemaVersion:1, sourceSeason:2026, sourceHash:'b'.repeat(64),
    sourceRetrievedAt:acquired, calculatedAt:acquired, collectionStatus:'current',
    personnelSourceHash:snapshot.sourceHash, personnelRetrievedAt:acquired,
    records:[{...player, identityStatus:'matched', cutoff:acquired,
      usage:{season:2026, type:'REG', week:1, cutoff:acquired, overall:{status:'unavailable'}}}]};
  return {snapshot, player, current};
}

test('compact briefing reads the supplied participation evidence', () => {
  const {snapshot, player, current} = fixture();
  const html = renderToStaticMarkup(createElement(PersonnelBriefing,
    {snapshot, players:[player], current, historical:null}));
  assert.match(html, /No verified 2026 earlier-week sample for these players/);
  assert.doesNotMatch(html, /2026 earlier-week participation is not verified/);
});

test('full participation disclosure receives that same supplied evidence', () => {
  const {snapshot, player, current} = fixture();
  const html = renderToStaticMarkup(createElement(PlayerUsage,
    {snapshot, player, current, historical:null}));
  assert.match(html, /No verified earlier-week appearances in this season/);
  assert.doesNotMatch(html, /Current-season participation is not verified/);
});

test('incompatible supplied evidence stays unavailable without static fallback', () => {
  const {snapshot, player, current} = fixture();
  const html = renderToStaticMarkup(createElement(PersonnelBriefing,
    {snapshot, players:[player], current:{...current, personnelSourceHash:'c'.repeat(64)}, historical:null}));
  assert.match(html, /2026 earlier-week participation is not verified/);
  assert.match(html, /Missing history does not mean zero/);
});

test('complete panel passes its selected evidence to nested views', () => {
  const {snapshot, player, current} = fixture();
  const game = {id:'2026_01_ATL_PIT', season:2026, type:'REG', week:1,
    home:'PIT', away:'ATL', kickoff:new Date(Date.now()+3600000).toISOString(), status:'scheduled'} as Game;
  const html = renderToStaticMarkup(createElement(PersonnelPanel, {game, evidence:{
    snapshot, collection:{status:'ok'}, current, historical:null,
    participationCollection:{status:'collected'}, quarterbackCollection:{status:'ok'},
    history:{schemaVersion:1, sourceHash:snapshot.sourceHash, retrievedAt:snapshot.retrievedAt,
      previousRetrievedAt:null, changes:[]},
    quarterback:{season:2026, retrievedAt:snapshot.retrievedAt, assetUpdatedAt:snapshot.assetUpdatedAt,
      sourceUrl:'https://example.com/source', sourceHash:'d'.repeat(64), teams:{PIT:{
        status:'available', recordedAt:snapshot.retrievedAt, listedFirst:player.playerId,
        quarterbacks:[{playerId:player.playerId, name:'Injected quarterback', rank:1}],
      }}},
  }}));
  assert.match(html, /Injected quarterback/);
  assert.match(html, /No verified 2026 earlier-week sample for these players/);
  assert.match(html, /No verified earlier-week appearances in this season/);
});

test('participation collection failure stays visible even when reports have expired', () => {
  const game = {id:'2026_01_ATL_PIT', season:2026, type:'REG', week:1,
    home:'PIT', away:'ATL', kickoff:new Date(Date.now()+3600000).toISOString(), status:'scheduled'} as Game;
  const evidence = {...staticPersonnelEvidence, participationCollection:{status:'failed'},
    snapshot:{...staticPersonnelEvidence.snapshot, retrievedAt:'2020-01-01T00:00:00Z', assetUpdatedAt:'2020-01-01T00:00:00Z'}};
  const html = renderToStaticMarkup(createElement(PersonnelPanel, {game, evidence}));
  assert.match(html, /Latest participation collection failed/);
  assert.match(html, /original collection date/);
});

test('withheld calculations explain missing participation without inventing a collection outage',()=>{
  const {snapshot}=fixture();
  const game={id:'2026_01_ATL_PIT',season:2026,type:'REG',week:1,home:'PIT',away:'ATL',
    kickoff:new Date(Date.now()+3600000).toISOString(),status:'scheduled'} as Game;
  const html=renderToStaticMarkup(createElement(PersonnelPanel,{game,evidence:{...staticPersonnelEvidence,
    snapshot,collection:{status:'ok'},quarterbackCollection:{status:'ok'},participationCollection:{status:'collected'},
    current:null,historical:null}}));
  assert.match(html,/Participation details are unavailable for this report set/);
  assert.match(html,/Injected player/);
  assert.doesNotMatch(html,/Latest participation collection failed/);
});
