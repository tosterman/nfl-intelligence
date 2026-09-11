import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import type {WeatherObjectStore} from './weather-publication';
import {readWeatherPartitionRoot,readWeatherPartitionSnapshot,readWeatherPartitionIndex,readWeatherGamePartitionObject,type WeatherObjectRef} from './weather-partition-store';

export const WEATHER_PARTITION_POINTER='weather/latest-v2.json';
const digest=(body:Buffer)=>createHash('sha256').update(body).digest('hex');

export async function readWeatherPartitionPointer(store:Pick<WeatherObjectStore,'read'>,now=Date.now()){
 const stored=await store.read(WEATHER_PARTITION_POINTER);
 if(!stored)return null;
 if(stored.body.length>4096||!stored.etag)throw Error('Invalid weather publication pointer');
 const pointer=JSON.parse(stored.body.toString());
 if(pointer?.schemaVersion!==2)throw Error('Unsupported weather publication pointer');
 const root=await readWeatherPartitionRoot(store,pointer.publication,now);
 if(pointer.generatedAt!==root.generatedAt)throw Error('Weather pointer time differs');
 return {root,publication:pointer.publication as WeatherObjectRef,etag:stored.etag,body:stored.body};
}

/** Storage transaction only. Caller must first prove raw-source replay and partition continuity. */
export async function publishWeatherPartitions(
 input:{publication:WeatherObjectRef;objects:Map<string,Buffer>},
 store:WeatherObjectStore,
 expectedPrevious:string|null,
 now=Date.now(),
){
 if(input.objects.size<1||input.objects.size>5000||[...input.objects.values()].reduce((n,b)=>n+b.length,0)>20_000_000)throw Error('Weather publication batch exceeds limit');
 for(const [identity,body] of input.objects){
  if(body.length<1||body.length>2_000_000||digest(body)!==identity)throw Error('Invalid weather publication object');
 }
 // Validate the prepared root and current snapshot before any storage mutation.
 const prepared={read:async(path:string)=>{
  const body=input.objects.get(path.replace(/^weather\/objects\//,''));
  return body?{body,etag:digest(body)}:store.read(path);
 }};
 const root=await readWeatherPartitionRoot(prepared,input.publication,now);
 const snapshot=await readWeatherPartitionSnapshot(prepared,root,now);
 const previous=await readWeatherPartitionPointer(store,now);
 const same=previous?.publication.sha256===input.publication.sha256;
 if((previous?.publication.sha256??null)!==expectedPrevious&&!same)throw Error('Weather pointer changed since continuity validation');
 if(previous&&(Date.parse(root.generatedAt)<Date.parse(previous.root.generatedAt)||
    (Date.parse(root.generatedAt)===Date.parse(previous.root.generatedAt)&&!same)))throw Error('Older or conflicting weather publication');
 const index=await readWeatherPartitionIndex(prepared,root);
 const priorIndex=previous?await readWeatherPartitionIndex(store,previous.root):{};
 if(Object.keys(priorIndex).some(id=>!Object.hasOwn(index,id)))throw Error('Retained weather game removed');
 if(snapshot.history.records.some(row=>!Object.hasOwn(index,row.gameId)))throw Error('Current weather game missing from history index');
 const checkedSources=new Set<string>();
 for(const [id,ref] of Object.entries(index)){
  const unchanged=priorIndex[id]?.sha256===ref.sha256&&priorIndex[id]?.bytes===ref.bytes;
  const anchors=snapshot.history.records.filter(row=>row.gameId===id);
  if(unchanged&&!anchors.length)continue;
  const partition=await readWeatherGamePartitionObject(prepared,root,id,ref);
  if(anchors.some(anchor=>!partition.history.records.some(row=>isDeepStrictEqual(row,anchor))))throw Error('Current weather anchor missing from retained partition');
  if(unchanged)continue;
  for(const source of Object.values(partition.sources)){
   if(checkedSources.has(source.sha256))continue;
   const stored=await prepared.read('weather/objects/'+source.sha256);
   if(!stored||stored.body.length!==source.bytes||digest(stored.body)!==source.sha256)throw Error('Referenced weather source missing or corrupt');
   checkedSources.add(source.sha256);
  }
 }
 let uploaded=0,reused=0;
 for(const [identity,body] of input.objects){
  const path='weather/objects/'+identity;
  const existing=await store.read(path);
  if(existing){
   if(!existing.body.equals(body))throw Error('Existing immutable weather object differs');
   reused++;continue;
  }
  let failure:unknown;
  try{await store.write(path,body);}catch(error){failure=error;}
  const actual=await store.read(path);
  if(!actual||!actual.body.equals(body))throw failure??Error('Weather immutable readback failed');
  uploaded++;
 }
 // Missing referenced snapshot/root objects cannot be masked by the preparation overlay.
 const publishedRoot=await readWeatherPartitionRoot(store,input.publication,now);
 await readWeatherPartitionSnapshot(store,publishedRoot,now);
 await readWeatherPartitionIndex(store,publishedRoot);
 const pointer=Buffer.from(JSON.stringify({schemaVersion:2,generatedAt:root.generatedAt,publication:input.publication}));
 if(!previous?.body.equals(pointer)){
  try{await store.write(WEATHER_PARTITION_POINTER,pointer,previous?.etag);}catch(error){
   const actual=await store.read(WEATHER_PARTITION_POINTER);
   if(!actual?.body.equals(pointer))throw error;
  }
 }
 const actual=await store.read(WEATHER_PARTITION_POINTER);
 if(!actual?.body.equals(pointer))throw Error('Weather publication superseded or readback failed');
 return {publication:input.publication,generatedAt:root.generatedAt,uploaded,reused};
}
