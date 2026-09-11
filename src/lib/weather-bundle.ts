import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import type {WeatherRecord} from './weather';
import {weatherHistoryForGame,type WeatherHistory} from './weather-history';

const digest=(body:Buffer)=>createHash('sha256').update(body).digest('hex');
const hash=(v:unknown)=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
const time=(v:unknown)=>typeof v==='string'&&/(Z|[+-]\d\d:\d\d)$/.test(v)&&Number.isFinite(Date.parse(v));
const object=(v:unknown)=>v!==null&&typeof v==='object'&&!Array.isArray(v);
type Context={id:string;season:number;kickoff:string|null;venue:string;neutral:boolean};
function sameVenue(a:unknown,b:unknown,key=''):boolean{
  if(typeof a==='number'&&typeof b==='number'&&['latitude','longitude','minlat','minlon','maxlat','maxlon'].includes(key)){
    // Bundlers can shorten JSON numeric literals. This is below 0.02 mm on Earth.
    return Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=1e-10;
  }
  if(object(a)&&object(b)){
    const left=a as Record<string,unknown>,right=b as Record<string,unknown>;
    return Object.keys(left).length===Object.keys(right).length&&Object.keys(left).every(k=>Object.hasOwn(right,k)&&sameVenue(left[k],right[k],k));
  }
  return isDeepStrictEqual(a,b);
}
export type WeatherBundle={
  weather:{collectionStartedAt:string;generatedAt:string;games:Record<string,WeatherRecord>};
  history:WeatherHistory;contexts:Record<string,Context>;venueRegistryHash:string;
  sourceHashes:string[];ledgerSha256:string;
};

export function assertWeatherContinuity(previous:WeatherBundle,next:WeatherBundle){
  if(Date.parse(next.weather.generatedAt)<Date.parse(previous.weather.generatedAt))throw Error('Weather collection regressed');
  const rows=new Map(next.history.records.map(row=>[row.hash,row]));
  if(previous.history.records.some(row=>!isDeepStrictEqual(rows.get(row.hash),row)))throw Error('Retained weather history was removed or changed');
  const sources=new Set(next.sourceHashes);
  if(previous.sourceHashes.some(hash=>!sources.has(hash)))throw Error('Retained weather source was removed');
}

export function boundWeatherRecord(bundle:WeatherBundle,game:Context,venues:Record<string,unknown>):WeatherRecord|undefined{
  const context=bundle.contexts[game.id],record=bundle.weather.games[game.id];
  if(!context||!record||!['id','season','kickoff','venue','neutral'].every(key=>context[key as keyof Context]===game[key as keyof Context]))return undefined;
  if(record.status==='available'){
    const approved=Object.hasOwn(venues,game.venue)?venues[game.venue]:null;
    if(game.neutral||!approved||!sameVenue(record.locationEvidence,approved))return undefined;
  }
  return record;
}

/** Verify transport/bundle consistency; raw NWS replay remains the trusted publisher's job. */
export function decodeWeatherBundle(raw:Buffer,now=Date.now()):WeatherBundle{
  if(raw.length>2_000_000)throw Error('Weather bundle too large');
  const envelope=JSON.parse(raw.toString()),meta=envelope?.manifest;
  if(!object(meta)||meta.schemaVersion!==1||meta.validatorVersion!=='weather-bundle-v1'||typeof envelope.payloadJson!=='string')throw Error('Unsupported weather bundle');
  const bytes=Buffer.from(envelope.payloadJson);
  if(bytes.length!==meta.payloadBytes||digest(bytes)!==meta.payloadSha256)throw Error('Weather payload integrity failure');
  if(!time(meta.collectionStartedAt)||!time(meta.generatedAt)||!Number.isFinite(now)||Date.parse(meta.collectionStartedAt)>Date.parse(meta.generatedAt)||Date.parse(meta.generatedAt)>now)throw Error('Invalid weather bundle time');
  if(!hash(meta.venueRegistryHash)||!hash(meta.ledgerSha256)||!Array.isArray(meta.sourceHashes)||meta.sourceHashes.length>4096||meta.sourceHashes.some((h:unknown)=>!hash(h))||new Set(meta.sourceHashes).size!==meta.sourceHashes.length)throw Error('Invalid weather evidence references');
  const payload=JSON.parse(envelope.payloadJson),weather=payload?.weather,history=payload?.history,contexts=payload?.contexts;
  if(payload?.schemaVersion!==1||payload.venueRegistryHash!==meta.venueRegistryHash||!object(weather)||weather.collectionStartedAt!==meta.collectionStartedAt||weather.generatedAt!==meta.generatedAt||!object(weather.games)||!object(contexts)||!object(history)||history.schemaVersion!==1||!Array.isArray(history.records)||history.records.length>20000)throw Error('Invalid weather payload schema');
  const ids=Object.keys(weather.games);
  if(ids.length>1000||ids.length!==Object.keys(contexts).length)throw Error('Invalid weather context scope');
  for(const row of history.records){
    if(!object(row)||!hash(row.hash)||!hash(row.locationHash)||!hash(row.sourceHash)||!meta.sourceHashes.includes(row.sourceHash)||typeof row.gameId!=='string'||typeof row.venue!=='string'||!time(row.kickoff)||!time(row.issuedAt)||!time(row.retrievedAt)||Date.parse(row.retrievedAt)>Date.parse(meta.generatedAt))throw Error('Invalid weather history record');
  }
  if(new Set(history.records.map((r:{hash:string})=>r.hash)).size!==history.records.length)throw Error('Duplicate weather history');
  for(const id of ids){
    const record=weather.games[id],context=contexts[id];
    if(!object(record)||!object(context)||context.id!==id||!Number.isInteger(context.season)||typeof context.neutral!=='boolean'||typeof context.venue!=='string'||(context.kickoff!==null&&!time(context.kickoff))||record.gameId!==id||record.venue!==context.venue||record.kickoff!==context.kickoff||!['available','unavailable'].includes(record.status))throw Error('Invalid weather game context');
    if(record.status==='available'){
      if(context.neutral||!hash(record.sourceHash)||!hash(record.pointHash)||!meta.sourceHashes.includes(record.sourceHash)||!meta.sourceHashes.includes(record.pointHash)||!time(record.retrievedAt)||Date.parse(record.retrievedAt)<Date.parse(meta.collectionStartedAt)||Date.parse(record.retrievedAt)>Date.parse(meta.generatedAt)||!weatherHistoryForGame(history,record,context))throw Error('Current weather lacks matching retained history');
    }
  }
  return {weather,history,contexts,venueRegistryHash:meta.venueRegistryHash,sourceHashes:meta.sourceHashes,ledgerSha256:meta.ledgerSha256};
}
