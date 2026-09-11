import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import type {WeatherObjectStore} from './weather-publication';
import type {WeatherHistory} from './weather-history';

type Reader=Pick<WeatherObjectStore,'read'>;
type JsonObject=Record<string,unknown>;
export type WeatherObjectRef={sha256:string;bytes:number};
export type WeatherPartitionRoot={generatedAt:string;snapshot:WeatherObjectRef;index:WeatherObjectRef};
const hash=(v:unknown):v is string=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
const time=(v:unknown):v is string=>typeof v==='string'&&/(Z|[+-]\d\d:\d\d)$/.test(v)&&Number.isFinite(Date.parse(v));
function object(value:unknown):JsonObject{
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('Invalid weather partition object');
 return value as JsonObject;
}
function reference(value:unknown):WeatherObjectRef{
 const r=object(value);
 if(Object.keys(r).length!==2||!hash(r.sha256)||!Number.isSafeInteger(r.bytes)||(r.bytes as number)<1||(r.bytes as number)>2_000_000)throw Error('Invalid weather partition reference');
 return {sha256:r.sha256,bytes:r.bytes as number};
}
async function readJson(store:Reader,ref:WeatherObjectRef,kind:string){
 const checked=reference(ref),stored=await store.read('weather/objects/'+checked.sha256);
 if(!stored||stored.body.length!==checked.bytes||createHash('sha256').update(stored.body).digest('hex')!==checked.sha256)throw Error('Weather partition integrity failure');
 const value=object(JSON.parse(stored.body.toString()));
 if(value.schemaVersion!==2||value.kind!==kind)throw Error('Unsupported weather partition schema');
 return value;
}

/** Transport integrity and shape only; approved venue/current-weather checks remain required. */
export async function readWeatherPartitionRoot(store:Reader,ref:WeatherObjectRef,now=Date.now()):Promise<WeatherPartitionRoot>{
 const root=await readJson(store,ref,'weather-publication');
 if(!time(root.generatedAt)||!Number.isFinite(now)||Date.parse(root.generatedAt)>now)throw Error('Invalid weather publication time');
 return {generatedAt:root.generatedAt,snapshot:reference(root.snapshot),index:reference(root.index)};
}

export async function readWeatherPartitionSnapshot(store:Reader,root:WeatherPartitionRoot){
 const snapshot=await readJson(store,root.snapshot,'weather-snapshot');
 const weather=object(snapshot.weather),contexts=object(snapshot.contexts),games=object(weather.games);
 if(!hash(snapshot.venueRegistryHash)||weather.generatedAt!==root.generatedAt||!time(weather.collectionStartedAt)||Date.parse(weather.collectionStartedAt)>Date.parse(root.generatedAt)||Object.keys(games).length>1000||!isDeepStrictEqual(Object.keys(games).sort(),Object.keys(contexts).sort()))throw Error('Invalid weather snapshot scope or time');
 return {weather,contexts,venueRegistryHash:snapshot.venueRegistryHash};
}

export async function readWeatherPartitionIndex(store:Reader,root:WeatherPartitionRoot){
 const index=await readJson(store,root.index,'weather-index'),games=object(index.games);
 if(Object.keys(games).length>5000)throw Error('Weather index exceeds game limit');
 const refs:Record<string,WeatherObjectRef>=Object.create(null);
 for(const [id,ref] of Object.entries(games)){
  if(!/^\d{4}_\d{2}_[A-Z]{2,3}_[A-Z]{2,3}$/.test(id))throw Error('Invalid weather index game');
  refs[id]=reference(ref);
 }
 return refs;
}

/** Reads no raw NWS sources. The Python publisher separately replays those exact bytes. */
export async function readWeatherGamePartition(store:Reader,root:WeatherPartitionRoot,gameId:string){
 const index=await readWeatherPartitionIndex(store,root);
 if(!Object.hasOwn(index,gameId))return null;
 const partition=await readJson(store,index[gameId],'weather-game-history');
 if(partition.gameId!==gameId||typeof partition.ledgerJson!=='string')throw Error('Weather partition game mismatch');
 const ledger:unknown=JSON.parse(partition.ledgerJson),history=object(partition.history),sources=object(partition.sources);
 if(!Array.isArray(ledger)||ledger.length>2000||history.schemaVersion!==1||!Array.isArray(history.records)||history.records.length!==ledger.length||Object.keys(sources).length>4096)throw Error('Invalid weather partition history');
 const sourceRefs:Record<string,WeatherObjectRef>=Object.create(null);
 for(const [identity,ref] of Object.entries(sources)){
  if(!hash(identity))throw Error('Invalid weather source identity');
  sourceRefs[identity]=reference(ref);
 }
 const rows=new Map<string,JsonObject>(),requiredSources=new Set<string>();
 for(const value of ledger){
  const row=object(value);
  if(row.gameId!==gameId||row.status!=='available'||!hash(row.hash)||rows.has(row.hash)||!hash(row.pointHash)||!hash(row.sourceHash)||!Object.hasOwn(sourceRefs,row.pointHash)||!Object.hasOwn(sourceRefs,row.sourceHash)||!time(row.kickoff)||!time(row.issuedAt)||!time(row.retrievedAt)||Date.parse(row.retrievedAt)>=Date.parse(row.kickoff)||Date.parse(row.retrievedAt)>Date.parse(root.generatedAt))throw Error('Invalid weather partition observation');
  rows.set(row.hash,row);requiredSources.add(row.pointHash);requiredSources.add(row.sourceHash);
 }
 if(requiredSources.size!==Object.keys(sourceRefs).length)throw Error('Unreferenced weather source');
 const seen=new Set<string>();
 const fields=['status','gameId','kickoff','venue','issuedAt','retrievedAt','periodStart','periodEnd','temperature','temperatureUnit','precipitationProbability','windSpeed','windDirection','summary','sourceHash','hash'];
 for(const value of history.records){
  const row=object(value),original=typeof row.hash==='string'?rows.get(row.hash):undefined;
  if(!original||!hash(row.hash)||seen.has(row.hash)||!hash(row.locationHash)||fields.some(key=>!isDeepStrictEqual(row[key]??null,original[key]??null)))throw Error('Weather compact history differs from ledger');
  seen.add(row.hash);
 }
 return {gameId,ledgerJson:partition.ledgerJson,history:history as unknown as WeatherHistory,sources:sourceRefs};
}
