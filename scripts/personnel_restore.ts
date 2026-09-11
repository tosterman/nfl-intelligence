import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {readPersonnelPublication,readPersonnelArchiveObject,type PersonnelObjectStore} from '../src/lib/personnel-publication';

const data=['site.json','games.csv','personnel.json','personnel-collection.json','quarterbacks.json',
  'quarterback-collection.json','participation-source.json','participation-collection.json',
  'personnel-changes.json','player-usage.json','season-participation.json'];
const reviews=['player-usage-source.csv.gz','player-identity-source.csv.gz','player-registry-source.json',
  'personnel-identity-audit.json','player-usage-audit.json'];
const digest=(raw:Buffer)=>createHash('sha256').update(raw).digest('hex');
function hash(value:unknown):asserts value is string{
  if(typeof value!=='string'||!/^[a-f0-9]{64}$/.test(value))throw Error('Invalid personnel source reference');
}
function canonical(value:unknown):string{
  const sort=(v:unknown):unknown=>Array.isArray(v)?v.map(sort):v!==null&&typeof v==='object'?
    Object.fromEntries(Object.entries(v).sort(([a],[b])=>a<b?-1:a>b?1:0).map(([k,x])=>[k,sort(x)])):v;
  return JSON.stringify(sort(value)).replace(/[^\x00-\x7f]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'))+'\n';
}

/** Select the current source closure only; older publications remain linked in storage. */
export async function restorePersonnelInputs(store:Pick<PersonnelObjectStore,'read'>){
  const selected=await readPersonnelPublication(store);
  if(!selected)throw Error('Personnel publication required before recurring restore');
  const files=new Map<string,Buffer>();let bytes=0;
  async function take(name:string){
    const existing=files.get(name);if(existing)return existing;
    const raw=await readPersonnelArchiveObject(store,selected!.root,name);bytes+=raw.length;
    if(bytes>64_000_000||files.size>=5000)throw Error('Personnel restore exceeds capacity');
    files.set(name,raw);return raw;
  }
  for(const name of data)await take('data/'+name);
  for(const name of reviews)await take('reviews/'+name);
  for(const name of Object.keys(selected.root.archive).filter(name=>/^scripts\/[a-zA-Z0-9_-]+\.py$/.test(name)))await take(name);
  const personnel=JSON.parse(files.get('data/personnel.json')!.toString());
  const quarterback=JSON.parse(files.get('data/quarterbacks.json')!.toString());
  const participation=JSON.parse(files.get('data/participation-source.json')!.toString());
  const pairs={'personnel.json':'snapshot','personnel-collection.json':'collection','quarterbacks.json':'quarterback',
    'quarterback-collection.json':'quarterbackCollection','participation-collection.json':'participationCollection',
    'personnel-changes.json':'history','player-usage.json':'historical','season-participation.json':'current'} as const;
  for(const [file,key]of Object.entries(pairs)){
    const published=selected.presentation.evidence[key];
    // An explicitly withheld derivation may retain older diagnostic files.
    if(published===null&&(key==='historical'||key==='current'))continue;
    const archived=JSON.parse(files.get('data/'+file)!.toString());
    if(key==='current')archived.collectionStatus=published&&typeof published==='object'?
      (published as Record<string,unknown>).collectionStatus:undefined;
    if(canonical(archived)!==canonical(published))throw Error('Restored inputs differ from selected presentation');
  }
  const edition=JSON.parse(files.get('data/site.json')!.toString());
  if(edition.source?.sha256!==digest(files.get('data/games.csv')!)||edition.source.sha256!==selected.presentation.scheduleHash)
    throw Error('Restored schedule bytes differ from publication');
  if(!Array.isArray(edition.games)||edition.games.length!==Object.keys(selected.presentation.contexts).length)
    throw Error('Restored edition scope differs');
  const ids=new Set<string>();
  for(const game of edition.games){
    const context=selected.presentation.contexts[game.id];
    if(ids.has(game.id)||!context||Object.entries(context).some(([key,value])=>game[key]!==value))
      throw Error('Restored game context differs');
    ids.add(game.id);
  }
  async function snapshot(value:unknown,folder:string){
    const encoded=Buffer.from(canonical(value)),id=digest(encoded);
    const raw=await take(`data/${folder}/${id}.snapshot.json.gz`);
    if(!gunzipSync(raw,{maxOutputLength:10_000_000}).equals(encoded))throw Error('Personnel snapshot does not replay');
    return id;
  }
  const capture=await snapshot(personnel,'personnel-sources');
  await snapshot(quarterback,'quarterback-sources');
  for(const [value,folder]of [[personnel,'personnel-sources'],[participation,'participation-sources']] as const){
    hash(value.sourceHash);
    const raw=gunzipSync(await take(`data/${folder}/${value.sourceHash}.csv.gz`),{maxOutputLength:120_000_000});
    if(digest(raw)!==value.sourceHash)throw Error('Personnel raw source differs');
  }
  hash(quarterback.sourceHash);
  const manifest=JSON.parse((await take(`data/quarterback-sources/${quarterback.sourceHash}.manifest.json`)).toString());
  if(manifest.sourceHash!==quarterback.sourceHash||!Array.isArray(manifest.chunks)||manifest.chunks.length>5000||
    !Number.isSafeInteger(manifest.bytes)||manifest.bytes<1||manifest.bytes>120_000_000)throw Error('Invalid quarterback reconstruction manifest');
  const reconstructed=createHash('sha256');let rawBytes=0;
  for(const id of manifest.chunks){
    hash(id);
    const raw=gunzipSync(await take(`data/quarterback-sources/raw-chunks/${id}.gz`),{maxOutputLength:120_000_000-rawBytes});
    rawBytes+=raw.length;
    if(digest(raw)!==id||rawBytes>120_000_000)throw Error('Quarterback source chunk differs');
    reconstructed.update(raw);
  }
  if(rawBytes!==manifest.bytes||reconstructed.digest('hex')!==quarterback.sourceHash)throw Error('Quarterback reconstruction differs');
  return {files,publication:selected.publication,capture,bytes,archiveFiles:Object.keys(selected.root.archive).length};
}
