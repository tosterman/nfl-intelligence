import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {staticPersonnelEvidence} from '../src/lib/personnel-static';
import {site} from '../src/lib/data';
import {publishPersonnelObjects,readPersonnelPublication,PERSONNEL_POINTER} from '../src/lib/personnel-publication';
const hash=(b:Buffer)=>createHash('sha256').update(b).digest('hex');
const now=Date.now();
function candidate(previous:{sha256:string;bytes:number}|null=null,when=now-1000,evidence=staticPersonnelEvidence){
  const objects=new Map<string,Buffer>();
  const retain=(value:unknown)=>{const body=Buffer.from(JSON.stringify(value)),sha256=hash(body);objects.set(sha256,body);return {sha256,bytes:body.length};};
  const g=site.games[0], context=Object.fromEntries(['id','season','week','type','home','away','kickoff','venue','neutral'].map(k=>[k,g[k as keyof typeof g]]));
  const generatedAt=new Date(when).toISOString();
  const presentation=retain({schemaVersion:1,kind:'personnel-presentation',generatedAt,scheduleHash:site.source.sha256,
    contexts:{[g.id]:context},evidence,
    derivation:{status:'compatible',cutoff:staticPersonnelEvidence.snapshot.retrievedAt,reason:null}});
  const archive={'data/personnel.json':retain(staticPersonnelEvidence.snapshot)};
  const publication=retain({schemaVersion:1,kind:'personnel-publication',generatedAt,presentation,archive,previous});
  return {publication,objects};
}
function store(){
  const files=new Map<string,Buffer>();let writes=0;
  return {files,get writes(){return writes;},read:async(path:string)=>{const body=files.get(path);return body?{body,etag:hash(body)}:null;},
    write:async(path:string,body:Buffer,etag?:string)=>{const prior=files.get(path);if(etag?!prior||hash(prior)!==etag:!!prior)throw Error('conflict');writes++;files.set(path,body);}};
}
test('publication retains complete objects, reads presentation only and retries without writes',async()=>{
  const input=candidate(),s=store();await publishPersonnelObjects(input,s,null,now);
  const count=s.writes,reads:string[]=[];
  const result=await readPersonnelPublication({...s,read:async p=>{reads.push(p);return s.read(p);}},now);
  assert.equal(result?.publication.sha256,input.publication.sha256);assert.equal(reads.length,3);
  await publishPersonnelObjects(input,s,null,now);assert.equal(s.writes,count);
});

test('equivalent acquisition timestamps cannot conceal a changed source identity',async()=>{
  const s=store(),first=candidate();await publishPersonnelObjects(first,s,null,now);
  const evidence=structuredClone(staticPersonnelEvidence);
  evidence.quarterback.retrievedAt=new Date(evidence.quarterback.retrievedAt).toISOString();
  evidence.quarterback.sourceHash='b'.repeat(64);
  await assert.rejects(publishPersonnelObjects(candidate(first.publication,now,evidence),s,first.publication.sha256,now));
  assert.equal((await readPersonnelPublication(s,now))?.publication.sha256,first.publication.sha256);
});
test('missing evidence and interrupted uploads never switch the pointer',async()=>{
  const input=candidate(),root=JSON.parse(input.objects.get(input.publication.sha256)!.toString());
  const objects=new Map(input.objects);objects.delete(root.archive['data/personnel.json'].sha256);
  const s=store();await assert.rejects(publishPersonnelObjects({...input,objects},s,null,now));assert.equal(s.writes,0);
  await assert.rejects(publishPersonnelObjects(input,{...s,write:async()=>{throw Error('offline');}},null,now));
  assert.equal(s.files.has(PERSONNEL_POINTER),false);
});
test('lost write responses require exact readback and competing writers are preserved',async()=>{
  const input=candidate(),s=store();await publishPersonnelObjects(input,{...s,write:async(...args)=>{await s.write(...args);throw Error('lost response');}},null,now);
  const next=candidate(input.publication,now),winner=Buffer.from('competing pointer');
  await assert.rejects(publishPersonnelObjects(next,{...s,write:async(path,body,etag)=>{
    if(path===PERSONNEL_POINTER)s.files.set(path,winner);await s.write(path,body,etag);
  }},input.publication.sha256,now));assert.deepEqual(s.files.get(PERSONNEL_POINTER),winner);
});
test('new publication links the accepted predecessor and preserves the old objects',async()=>{
  const s=store(),first=candidate();await publishPersonnelObjects(first,s,null,now);
  const old=new Map(s.files);await assert.rejects(publishPersonnelObjects(candidate(null,now),s,first.publication.sha256,now));
  const next=candidate(first.publication,now);await publishPersonnelObjects(next,s,first.publication.sha256,now);
  for(const [path,body]of old)if(path!==PERSONNEL_POINTER)assert.deepEqual(s.files.get(path),body);
  assert.equal((await readPersonnelPublication(s,now))?.root.previous?.sha256,first.publication.sha256);
});
