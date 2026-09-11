import {createHash} from 'node:crypto';

export type WeatherObjectStore = {
  read(path:string):Promise<{body:Buffer;etag:string}|null>;
  // Undefined version means create-only, never unconditional overwrite.
  write(path:string,body:Buffer,etag?:string):Promise<void>;
};
const hash=(body:Buffer)=>createHash('sha256').update(body).digest('hex');
const LATEST='weather/latest.json';
const MAX_TOTAL_BYTES=20_000_000;
const validHash=(value:unknown):value is string=>typeof value==='string'&&/^[a-f0-9]{64}$/.test(value);
const validTime=(value:unknown):value is string=>typeof value==='string'&&/(Z|[+-]\d\d:\d\d)$/.test(value)&&Number.isFinite(Date.parse(value));

function parsePointer(body:Buffer){
  if(body.length>4096)throw Error('Invalid weather pointer');
  const value=JSON.parse(body.toString());
  if(!value||value.schemaVersion!==1||!validTime(value.generatedAt)||!validHash(value.manifestHash))throw Error('Invalid weather pointer');
  return {generatedAt:value.generatedAt as string,manifestHash:value.manifestHash as string,frozenForMigration:value.frozenForMigration===true};
}

/** Hash integrity only; callers still validate the weather schema and source freshness. */
export async function readWeatherObjects(store:Pick<WeatherObjectStore,'read'>,indices?:number[]){
  const pointer=await store.read(LATEST);
  if(!pointer)return null;
  const ref=parsePointer(pointer.body);
  const raw=await store.read(`weather/manifests/${ref.manifestHash}.json`);
  if(!raw||raw.body.length>400_000||hash(raw.body)!==ref.manifestHash)throw Error('Weather manifest integrity failure');
  const manifest=JSON.parse(raw.body.toString());
  if(!manifest||manifest.schemaVersion!==1||manifest.generatedAt!==ref.generatedAt||!Array.isArray(manifest.objects)||!manifest.objects.length||manifest.objects.length>2048)throw Error('Invalid weather manifest');
  const entries: {sha256:string;bytes:number}[]=[];
  for(const entry of manifest.objects){
    if(!entry||!validHash(entry.sha256)||!Number.isSafeInteger(entry.bytes)||entry.bytes<1||entry.bytes>10_000_000)throw Error('Invalid weather manifest object');
    entries.push({sha256:entry.sha256,bytes:entry.bytes});
  }
  if(new Set(entries.map(e=>e.sha256)).size!==entries.length||entries.reduce((n,e)=>n+e.bytes,0)>MAX_TOTAL_BYTES)throw Error('Invalid weather manifest size or duplicates');
  const selected=indices??entries.map((_,i)=>i);
  if(new Set(selected).size!==selected.length||selected.some(i=>!Number.isInteger(i)||i<0||i>=entries.length))throw Error('Invalid weather object selection');
  const objects:Buffer[]=[];
  for(const index of selected){
    const entry=entries[index],result=await store.read(`weather/objects/${entry.sha256}`);
    if(!result||result.body.length!==entry.bytes||hash(result.body)!==entry.sha256)throw Error('Weather object integrity failure');
    objects.push(result.body);
  }
  return {...ref,entries,objects};
}

async function immutable(path:string,body:Buffer,store:WeatherObjectStore){
  let failure:unknown;
  try{await store.write(path,body);}catch(error){failure=error;}
  const actual=await store.read(path);
  if(!actual || !actual.body.equals(body)) throw failure ?? Error('Weather object readback differs');
}

/** Storage primitive only: callers must validate weather evidence and history continuity. */
export async function publishWeatherObjects(objects:Buffer[],generatedAt:string,store:WeatherObjectStore,validatedPrevious?:string|null){
  const timestamp=Date.parse(generatedAt);
  if(!Number.isFinite(timestamp)||!/(Z|[+-]\d\d:\d\d)$/.test(generatedAt)||!objects.length||objects.length>2048 ||
    objects.some(body=>body.length===0||body.length>10_000_000)||objects.reduce((n,b)=>n+b.length,0)>MAX_TOTAL_BYTES) throw Error('Invalid weather publication input');
  const entries=objects.map(body=>({sha256:hash(body),bytes:body.length}));
  if(new Set(entries.map(entry=>entry.sha256)).size!==entries.length) throw Error('Duplicate weather objects');
  const manifest=Buffer.from(JSON.stringify({schemaVersion:1,generatedAt,objects:entries}));
  const manifestHash=hash(manifest);
  const previous=await store.read(LATEST);
  if(validatedPrevious!==undefined&&(previous?parsePointer(previous.body).manifestHash:null)!==validatedPrevious)throw Error('Weather pointer changed since history validation');
  if(previous){
    if(!previous.etag)throw Error('Invalid weather pointer');
    const pointer=parsePointer(previous.body);
    if(pointer.frozenForMigration)throw Error('Legacy weather publication is frozen for migration');
    const priorTime=Date.parse(pointer.generatedAt);
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
