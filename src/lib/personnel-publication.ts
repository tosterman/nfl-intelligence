import {createHash} from 'node:crypto';
import {decodePersonnelPresentation} from './personnel-presentation';

export type PersonnelObjectStore={read(path:string):Promise<{body:Buffer;etag:string}|null>;
  write(path:string,body:Buffer,etag?:string):Promise<void>};
export type PersonnelRef={sha256:string;bytes:number};
export type PersonnelRoot={schemaVersion:1;kind:'personnel-publication';generatedAt:string;
  presentation:PersonnelRef;archive:Record<string,PersonnelRef>;previous:PersonnelRef|null};
export const PERSONNEL_POINTER='personnel/latest.json';
const hash=(body:Buffer)=>createHash('sha256').update(body).digest('hex');
const path=(ref:PersonnelRef)=>`personnel/objects/${ref.sha256}`;
function requireValue(value:unknown):asserts value {if(!value)throw Error('Invalid personnel publication');}
function ref(raw:unknown):PersonnelRef{
  requireValue(raw!==null&&typeof raw==='object'&&!Array.isArray(raw));
  const value=raw as Record<string,unknown>;
  requireValue(Object.keys(value).length===2&&typeof value.sha256==='string'&&/^[a-f0-9]{64}$/.test(value.sha256)&&
    Number.isSafeInteger(value.bytes)&&Number(value.bytes)>0&&Number(value.bytes)<=10_000_000);
  return value as PersonnelRef;
}
function timestamp(value:unknown,now:number):value is string{
  return typeof value==='string'&&/(Z|[+-]\d\d:\d\d)$/.test(value)&&Number.isFinite(Date.parse(value))&&Date.parse(value)<=now;
}
async function object(store:Pick<PersonnelObjectStore,'read'>,reference:PersonnelRef){
  const value=await store.read(path(reference));
  if(!value||value.body.length!==reference.bytes||hash(value.body)!==reference.sha256)throw Error('Personnel object integrity failure');
  return value.body;
}
function root(body:Buffer,now:number):PersonnelRoot{
  requireValue(body.length<=1_000_000);
  const value=JSON.parse(body.toString());
  requireValue(value?.schemaVersion===1&&value.kind==='personnel-publication'&&timestamp(value.generatedAt,now));
  ref(value.presentation);if(value.previous!==null)ref(value.previous);
  requireValue(value.archive&&typeof value.archive==='object'&&!Array.isArray(value.archive));
  const entries=Object.entries(value.archive);requireValue(entries.length>0&&entries.length<=5000);
  for(const [name,entry]of entries){
    requireValue(name.length<=240&&/^(data|reviews|scripts)\/[a-zA-Z0-9_./-]+$/.test(name)&&
      !name.split('/').some(part=>part===''||part==='.'||part==='..'));
    ref(entry);
  }
  return value as PersonnelRoot;
}

export async function readPersonnelPublication(store:Pick<PersonnelObjectStore,'read'>,now=Date.now()){
  const current=await store.read(PERSONNEL_POINTER);if(!current)return null;
  requireValue(current.body.length<=4096&&current.etag);
  const pointer=JSON.parse(current.body.toString());
  requireValue(pointer?.schemaVersion===1&&timestamp(pointer.generatedAt,now));
  const publication=ref(pointer.publication), selected=root(await object(store,publication),now);
  requireValue(selected.generatedAt===pointer.generatedAt);
  const presentation=decodePersonnelPresentation(await object(store,selected.presentation),selected.presentation,now);
  requireValue(presentation.generatedAt===selected.generatedAt);
  return {publication,root:selected,presentation,etag:current.etag};
}

export async function readPersonnelArchiveObject(store:Pick<PersonnelObjectStore,'read'>,selected:PersonnelRoot,name:string){
  const reference=selected.archive[name];
  if(!reference)throw Error('Personnel archive input missing');
  return object(store,reference);
}

/** Transaction only. The caller must replay source/derivation evidence and select its complete archive. */
export async function publishPersonnelObjects(input:{publication:PersonnelRef;objects:Map<string,Buffer>},
  store:PersonnelObjectStore,expectedPrevious:string|null,now=Date.now()){
  ref(input.publication);requireValue(input.objects.size<=5002);
  let total=0;
  for(const [identity,body]of input.objects){
    requireValue(body.length>0&&body.length<=10_000_000&&hash(body)===identity);total+=body.length;
  }
  requireValue(total<=64_000_000);
  const prepared={read:async(name:string)=>{
    const candidate=input.objects.get(name.replace(/^personnel\/objects\//,''));
    return candidate?{body:candidate,etag:hash(candidate)}:store.read(name);
  }};
  const selected=root(await object(prepared,input.publication),now);
  const presentation=decodePersonnelPresentation(await object(prepared,selected.presentation),selected.presentation,now);
  requireValue(presentation.generatedAt===selected.generatedAt);
  const previous=await readPersonnelPublication(store,now);
  const identical=previous?.publication.sha256===input.publication.sha256;
  if(!identical){
    requireValue((previous?.publication.sha256??null)===expectedPrevious);
    requireValue(previous?selected.previous?.sha256===previous.publication.sha256&&selected.previous.bytes===previous.publication.bytes:selected.previous===null);
    if(previous){
      requireValue(Date.parse(selected.generatedAt)>Date.parse(previous.root.generatedAt));
      for(const key of ['snapshot','quarterback'] as const){
        const before=previous.presentation.evidence[key],after=presentation.evidence[key];
        requireValue(Date.parse(after.retrievedAt)>=Date.parse(before.retrievedAt)&&Date.parse(after.assetUpdatedAt)>=Date.parse(before.assetUpdatedAt));
        if(Date.parse(after.retrievedAt)===Date.parse(before.retrievedAt))requireValue(after.sourceHash===before.sourceHash);
      }
    }
  }
  const references=[input.publication,selected.presentation,...Object.values(selected.archive)];
  const referenced=new Set(references.map(r=>r.sha256));
  requireValue([...input.objects.keys()].every(key=>referenced.has(key)));
  // Resolve every reference before writing anything, including reused archives.
  for(const reference of references)await object(prepared,reference);
  let uploaded=0,reused=0;
  for(const [identity,body]of input.objects){
    const name=`personnel/objects/${identity}`, prior=await store.read(name);
    if(prior){requireValue(prior.body.equals(body));reused++;continue;}
    let failure:unknown;
    try{await store.write(name,body);}catch(error){failure=error;}
    const actual=await store.read(name);
    if(!actual?.body.equals(body))throw failure??Error('Personnel object readback differs');
    uploaded++;
  }
  for(const reference of references)await object(store,reference);
  if(!identical){
    const pointer=Buffer.from(JSON.stringify({schemaVersion:1,generatedAt:selected.generatedAt,publication:input.publication}));
    try{await store.write(PERSONNEL_POINTER,pointer,previous?.etag);}catch(error){
      if(!(await store.read(PERSONNEL_POINTER))?.body.equals(pointer))throw error;
    }
  }
  const actual=await readPersonnelPublication(store,now);
  requireValue(actual?.publication.sha256===input.publication.sha256);
  return {publication:input.publication,uploaded,reused};
}
