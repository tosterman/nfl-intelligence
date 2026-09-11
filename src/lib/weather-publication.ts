import {createHash} from 'node:crypto';

export type WeatherObjectStore = {
  read(path:string):Promise<{body:Buffer;etag:string}|null>;
  // Undefined version means create-only, never unconditional overwrite.
  write(path:string,body:Buffer,etag?:string):Promise<void>;
};
const hash=(body:Buffer)=>createHash('sha256').update(body).digest('hex');
const LATEST='weather/latest.json';

async function immutable(path:string,body:Buffer,store:WeatherObjectStore){
  let failure:unknown;
  try{await store.write(path,body);}catch(error){failure=error;}
  const actual=await store.read(path);
  if(!actual || !actual.body.equals(body)) throw failure ?? Error('Weather object readback differs');
}

/** Storage primitive only: callers must validate weather evidence and history continuity. */
export async function publishWeatherObjects(objects:Buffer[],generatedAt:string,store:WeatherObjectStore){
  const timestamp=Date.parse(generatedAt);
  if(!Number.isFinite(timestamp)||!/(Z|[+-]\d\d:\d\d)$/.test(generatedAt)||!objects.length||objects.length>2048 ||
    objects.some(body=>body.length===0||body.length>10_000_000)) throw Error('Invalid weather publication input');
  const entries=objects.map(body=>({sha256:hash(body),bytes:body.length}));
  if(new Set(entries.map(entry=>entry.sha256)).size!==entries.length) throw Error('Duplicate weather objects');
  const manifest=Buffer.from(JSON.stringify({schemaVersion:1,generatedAt,objects:entries}));
  const manifestHash=hash(manifest);
  const previous=await store.read(LATEST);
  if(previous){
    if(!previous.etag||previous.body.length>4096)throw Error('Invalid weather pointer');
    const pointer=JSON.parse(previous.body.toString());
    const priorTime=Date.parse(pointer.generatedAt);
    if(pointer.schemaVersion!==1||!Number.isFinite(priorTime)||! /^[a-f0-9]{64}$/.test(pointer.manifestHash))throw Error('Invalid weather pointer');
    if(priorTime>timestamp)throw Error('Cannot publish older weather');
    if(priorTime===timestamp&&pointer.manifestHash!==manifestHash)throw Error('Conflicting weather acquisition');
  }
  for(let i=0;i<objects.length;i++)await immutable(`weather/objects/${entries[i].sha256}`,objects[i],store);
  await immutable(`weather/manifests/${manifestHash}.json`,manifest,store);
  const pointer=Buffer.from(JSON.stringify({schemaVersion:1,generatedAt,manifestHash}));
  if(previous?.body.equals(pointer))return manifestHash;
  try{await store.write(LATEST,pointer,previous?.etag);}catch(error){
    // A committed pointer with a lost response is success only after exact readback.
    const actual=await store.read(LATEST);
    if(!actual?.body.equals(pointer))throw error;
  }
  const actual=await store.read(LATEST);
  if(!actual?.body.equals(pointer))throw Error('Weather pointer readback differs or publication superseded');
  return manifestHash;
}
