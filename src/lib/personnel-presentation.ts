import {createHash} from 'node:crypto';
import type {PersonnelEvidence} from './personnel-evidence';
import type {Game} from './types';
import {teams} from './teams';

const fields=['id','season','week','type','home','away','kickoff','venue','neutral'] as const;
type Context=Pick<Game,typeof fields[number]>;
export type PersonnelPresentation={schemaVersion:1;kind:'personnel-presentation';generatedAt:string;
  scheduleHash:string;contexts:Record<string,Context>;evidence:PersonnelEvidence;
  derivation:{status:'compatible'|'unavailable';cutoff:string;reason:string|null}};
function requireValue(value:unknown):asserts value {if(!value)throw Error('Invalid personnel presentation');}
function object(value:unknown):Record<string,unknown>{
  requireValue(value!==null&&typeof value==='object'&&!Array.isArray(value));return value as Record<string,unknown>;
}
const text=(v:unknown,max=200):v is string=>typeof v==='string'&&v.length>0&&v.length<=max;
const hash=(v:unknown)=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
const time=(v:unknown):v is string=>typeof v==='string'&&/(Z|[+-]\d\d:\d\d)$/.test(v)&&Number.isFinite(Date.parse(v));
const team=(v:unknown)=>typeof v==='string'&&Object.hasOwn(teams,v);
const nullableText=(v:unknown)=>v===null||text(v,2000);
function rows(value:unknown,max:number):unknown[]{requireValue(Array.isArray(value)&&value.length<=max);return value;}
function identity(row:Record<string,unknown>){return JSON.stringify(['season','type','week','team','playerId','name'].map(k=>row[k]));}

/** Presentation integrity/schema only; publisher must retain verified raw evidence. */
export function decodePersonnelPresentation(body:Buffer,reference:{sha256:string;bytes:number},now=Date.now()):PersonnelPresentation{
  requireValue(Number.isFinite(now)&&body.length>0&&body.length<=2_000_000&&body.length===reference.bytes&&
    hash(reference.sha256)&&createHash('sha256').update(body).digest('hex')===reference.sha256);
  const value=object(JSON.parse(body.toString('utf8')));
  requireValue(value.schemaVersion===1&&value.kind==='personnel-presentation'&&time(value.generatedAt)&&
    Date.parse(value.generatedAt)<=now&&hash(value.scheduleHash));
  const generated=Date.parse(value.generatedAt), contexts=object(value.contexts), evidence=object(value.evidence);
  requireValue(Object.keys(contexts).length>0&&Object.keys(contexts).length<=1000);
  const snapshot=object(evidence.snapshot), qb=object(evidence.quarterback), history=object(evidence.history);
  requireValue(snapshot.status==='available'&&Number.isInteger(snapshot.season)&&qb.season===snapshot.season);
  for(const [id,raw] of Object.entries(contexts)){
    const c=object(raw);
    requireValue(/^\d{4}_\d{2}_[A-Z]{2,3}_[A-Z]{2,3}$/.test(id)&&c.id===id&&c.season===snapshot.season&&
      Number.isInteger(c.week)&&Number(c.week)>=1&&Number(c.week)<=22&&
      ['REG','WC','DIV','CON','SB'].includes(String(c.type))&&team(c.home)&&team(c.away)&&c.home!==c.away&&
      (c.kickoff===null||time(c.kickoff))&&text(c.venue)&&typeof c.neutral==='boolean');
  }
  for(const source of [snapshot,qb]){
    requireValue(hash(source.sourceHash)&&time(source.retrievedAt)&&time(source.assetUpdatedAt)&&
      Date.parse(source.assetUpdatedAt)<=Date.parse(source.retrievedAt)&&Date.parse(source.retrievedAt)<=generated);
  }
  const players=rows(snapshot.players,5000).map(object), identities=new Set<string>(), scopes=new Set<string>();
  for(const player of players){
    requireValue(player.season===snapshot.season&&['REG','POST'].includes(String(player.type))&&
      Number.isInteger(player.week)&&Number(player.week)>=1&&Number(player.week)<=22&&team(player.team)&&
      typeof player.playerId==='string'&&/^\d{2}-\d{7}$/.test(player.playerId)&&text(player.name)&&text(player.position)&&
      ['reportStatus','practiceStatus','reportInjury','practiceInjury','practiceSecondaryInjury'].every(k=>nullableText(player[k])));
    const scope=JSON.stringify(['season','type','week','team','playerId'].map(k=>player[k]));
    requireValue(!scopes.has(scope));scopes.add(scope);identities.add(identity(player));
  }
  requireValue(qb.sourceUrl===`https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_${qb.season}.csv`);
  const roles=object(qb.teams);requireValue(Object.keys(roles).length<=32);
  for(const [key,raw] of Object.entries(roles)){
    const role=object(raw);requireValue(team(key)&&['available','unavailable'].includes(String(role.status))&&
      (role.recordedAt===null||(time(role.recordedAt)&&Date.parse(role.recordedAt)<=Date.parse(String(qb.retrievedAt))))&&
      (role.listedFirst===null||text(role.listedFirst)));
    for(const rawPlayer of rows(role.quarterbacks,20)){
      const player=object(rawPlayer);requireValue(text(player.playerId)&&text(player.name)&&Number.isInteger(player.rank)&&Number(player.rank)>=1);
    }
  }
  for(const [key,allowed] of [['collection',['ok','unavailable']],['quarterbackCollection',['ok','unavailable']],
    ['participationCollection',['collected','failed']]] as const){
    const state=object(evidence[key]);requireValue(allowed.includes(state.status as never));
    for(const key of ['checkedAt','attemptedAt','retrievedAt'])if(Object.hasOwn(state,key))requireValue(time(state[key])&&Date.parse(state[key])<=generated);
  }
  requireValue(history.schemaVersion===1&&history.sourceHash===snapshot.sourceHash&&history.retrievedAt===snapshot.retrievedAt&&
    (history.previousRetrievedAt===null||(time(history.previousRetrievedAt)&&Date.parse(history.previousRetrievedAt)<Date.parse(String(history.retrievedAt)))));
  for(const raw of rows(history.changes,10000)){
    const change=object(raw);requireValue(change.season===snapshot.season&&['REG','POST'].includes(String(change.type))&&
      Number.isInteger(change.week)&&team(change.team)&&text(change.playerId)&&text(change.playerName)&&nullableText(change.position)&&
      ['first-observed','no-longer-present','changed'].includes(String(change.kind))&&change.eventTime===null&&
      change.observedAfter===history.previousRetrievedAt&&change.observedBy===history.retrievedAt&&history.previousRetrievedAt!==null);
    for(const [key,rawPair] of Object.entries(object(change.fields))){
      const pair=object(rawPair);requireValue(['name','position','reportStatus','practiceStatus','reportInjury','practiceInjury','practiceSecondaryInjury'].includes(key)&&nullableText(pair.before)&&nullableText(pair.after));
    }
  }
  const derivation=object(value.derivation);
  requireValue(['compatible','unavailable'].includes(String(derivation.status))&&time(derivation.cutoff)&&Date.parse(derivation.cutoff)<=generated);
  if(derivation.status==='unavailable')requireValue(text(derivation.reason,1000)&&evidence.historical===null&&evidence.current===null);
  else{
    requireValue(derivation.reason===null);
    for(const raw of [evidence.historical,evidence.current]){
      const usage=object(raw);requireValue(usage.personnelSourceHash===snapshot.sourceHash&&usage.personnelRetrievedAt===snapshot.retrievedAt&&
        time(usage.calculatedAt)&&Date.parse(usage.calculatedAt)>=Date.parse(String(snapshot.retrievedAt))&&Date.parse(usage.calculatedAt)<=generated);
      const usageRows=rows(usage.records,5000).map(object), keys=usageRows.map(identity);
      requireValue(keys.length===identities.size&&new Set(keys).size===keys.length&&keys.every(k=>identities.has(k)));
    }
  }
  return value as unknown as PersonnelPresentation;
}

export function personnelEvidenceForGame(value:PersonnelPresentation,game:Game):PersonnelEvidence|null{
  const context=value.contexts[game.id];
  return context&&fields.every(key=>context[key]===game[key])?value.evidence:null;
}
