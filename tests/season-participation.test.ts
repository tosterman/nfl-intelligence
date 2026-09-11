import { test } from 'node:test';
import assert from 'node:assert/strict';
import { seasonParticipation } from '../src/lib/season-participation';
import type { PersonnelSnapshot, PlayerReport } from '../src/lib/personnel';
const player = {playerId:'p',name:'Player',team:'PIT',season:2026,week:2,type:'REG'} as PlayerReport;
const snapshot = {sourceHash:'a'.repeat(64),retrievedAt:'2026-09-16T00:00:00Z'} as PersonnelSnapshot;
const cutoff = snapshot.retrievedAt;
const game = {gameId:'2026_01_A_PIT',team:'PIT',kickoff:'2026-09-10T00:00:00Z'};
const usage = {season:2026,week:2,type:'REG',cutoff,overall:{status:'available',appearances:1,lastAppearance:game.kickoff,weightedShares:{offense_pct:.5,defense_pct:0,st_pct:.1},games:[game]}};
const artifact = {schemaVersion:1,sourceSeason:2026,sourceHash:'b'.repeat(64),sourceRetrievedAt:cutoff,calculatedAt:cutoff,personnelSourceHash:snapshot.sourceHash,personnelRetrievedAt:cutoff,collectionStatus:'current',records:[{...player,identityStatus:'matched',cutoff,usage}]};
const now = Date.parse('2026-09-17T00:00:00Z');
test('current-season sample binds exact report and separates team appearances', () => {
  assert.equal(seasonParticipation(artifact,snapshot,player,now)?.currentTeamAppearances,1);
  const transfer = {...artifact,records:[{...artifact.records[0],usage:{...usage,overall:{...usage.overall,games:[{...game,team:'ATL'}]}}}]};
  assert.equal(seasonParticipation(transfer,snapshot,player,now)?.formerTeamAppearances,1);
  for (const change of [{week:1},{season:2025},{name:'Other'}]) assert.equal(seasonParticipation(artifact,snapshot,{...player,...change},now),null);
});
test('unresolved identity, future collection, embargo and malformed counts are withheld', () => {
  const row = artifact.records[0];
  for (const changed of [
    {...artifact,records:[{...row,identityStatus:'identifier-mismatch'}]},
    {...artifact,calculatedAt:'2027-01-01T00:00:00Z'},
    {...artifact,records:[row,row]},
    {...artifact,records:[{...row,usage:{...usage,overall:{...usage.overall,appearances:2}}}]},
    {...artifact,records:[{...row,usage:{...usage,overall:{...usage.overall,games:[{...game,kickoff:cutoff}]}}}]},
  ]) assert.equal(seasonParticipation(changed,snapshot,player,now),null);
});
test('missing appearances stay unavailable and retained acquisition stays dated', () => {
  const value = seasonParticipation({...artifact,collectionStatus:'retained',records:[{...artifact.records[0],usage:{...usage,overall:{status:'unavailable'}}}]},snapshot,player,now);
  assert.equal(value?.appearances,null); assert.equal(value?.shares,null);
  assert.equal(value?.retained,true); assert.equal(value?.sourceRetrievedAt,cutoff);
});
