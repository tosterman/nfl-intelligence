import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {decodePersonnelPresentation, personnelEvidenceForGame} from '../src/lib/personnel-presentation';
import type {Game} from '../src/lib/types';

const now=Date.parse('2026-09-11T19:00:00Z');
function fixture(){
  const at='2026-09-11T18:00:00Z', hash='a'.repeat(64);
  const game={id:'2026_01_ATL_PIT',season:2026,week:1,type:'REG',home:'PIT',away:'ATL',
    kickoff:'2026-09-13T17:00:00Z',venue:'Acrisure Stadium',neutral:false};
  const player={season:2026,week:1,type:'REG',team:'PIT',playerId:'00-1234567',name:'Example Player',position:'WR',
    reportStatus:'Questionable',practiceStatus:null,reportInjury:null,practiceInjury:null,practiceSecondaryInjury:null};
  const usage={personnelSourceHash:hash,personnelRetrievedAt:at,calculatedAt:at,records:[{...player}]};
  return {schemaVersion:1,kind:'personnel-presentation',generatedAt:at,scheduleHash:hash,
    contexts:{[game.id]:game},derivation:{status:'compatible',cutoff:at,reason:null},evidence:{
      snapshot:{schemaVersion:1,status:'available',season:2026,sourceHash:hash,retrievedAt:at,assetUpdatedAt:at,players:[player]},
      quarterback:{season:2026,sourceHash:hash,retrievedAt:at,assetUpdatedAt:at,
        sourceUrl:'https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2026.csv',teams:{}},
      collection:{status:'ok'},quarterbackCollection:{status:'ok'},participationCollection:{status:'collected'},
      history:{schemaVersion:1,sourceHash:hash,retrievedAt:at,previousRetrievedAt:null,changes:[]},
      current:structuredClone(usage),historical:structuredClone(usage),
    }};
}
function decode(value:unknown){
  const body=Buffer.from(JSON.stringify(value));
  return decodePersonnelPresentation(body,{sha256:createHash('sha256').update(body).digest('hex'),bytes:body.length},now);
}
test('reader binds every game context and returns the single selected evidence set',()=>{
  const input=fixture(), decoded=decode(input), game=Object.values(input.contexts)[0] as Game;
  assert.equal(personnelEvidenceForGame(decoded,game),decoded.evidence);
  for(const changed of [{kickoff:'2026-09-14T17:00:00Z'},{neutral:true},{venue:'Other'},{home:'BAL'},{week:2}])
    assert.equal(personnelEvidenceForGame(decoded,{...game,...changed}),null);
});
test('reader rejects corrupt transport and future publications',()=>{
  assert.throws(()=>decodePersonnelPresentation(Buffer.from('{}'),{sha256:'a'.repeat(64),bytes:2},now));
  const value=fixture();value.generatedAt='2026-09-12T00:00:00Z';assert.throws(()=>decode(value));
});
test('reader rejects mixed participation, duplicate report identities and unsafe source links',()=>{
  let value=fixture();value.evidence.current.personnelSourceHash='b'.repeat(64);assert.throws(()=>decode(value));
  value=fixture();value.evidence.snapshot.players.push(value.evidence.snapshot.players[0]);assert.throws(()=>decode(value));
  value=fixture();const duplicate={...value.evidence.snapshot.players[0],name:'Conflicting Name'};
  value.evidence.snapshot.players.push(duplicate);value.evidence.current.records.push(duplicate);value.evidence.historical.records.push(duplicate);
  assert.throws(()=>decode(value));
  value=fixture();value.evidence.quarterback.sourceUrl='javascript:alert(1)';assert.throws(()=>decode(value));
});
test('reader rejects malformed report changes before a component sees them',()=>{
  const value=fixture();(value.evidence.history.changes as unknown[]).push({fields:null});assert.throws(()=>decode(value));
});
test('degraded package preserves collection failure with no invented participation',()=>{
  const value=fixture();Object.assign(value.derivation,{status:'unavailable',reason:'No common cutoff'});
  Object.assign(value.evidence,{current:null,historical:null});value.evidence.quarterbackCollection.status='unavailable';
  assert.equal(decode(value).evidence.current,null);
  Object.assign(value.evidence,{historical:fixture().evidence.historical});assert.throws(()=>decode(value));
});
