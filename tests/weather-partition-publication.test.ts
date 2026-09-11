import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {publishWeatherPartitions,readWeatherPartitionPointer,WEATHER_PARTITION_POINTER} from '../src/lib/weather-partition-publication';
const hash=(b:Buffer)=>createHash('sha256').update(b).digest('hex');
const raw=JSON.parse(execFileSync('python',['-c',"import sys,json,base64;sys.path.insert(0,'scripts');from weather_partitions import build_partitions;r=build_partitions();print(json.dumps({'publication':r['publication'],'objects':{h:base64.b64encode(b).decode() for h,b in r['objects'].items()}}))"],{maxBuffer:10_000_000}).toString());
const input={publication:raw.publication,objects:new Map<string,Buffer>(Object.entries(raw.objects).map(([h,b])=>[h,Buffer.from(b as string,'base64')]))};
const now=Date.parse(JSON.parse(input.objects.get(input.publication.sha256)!.toString()).generatedAt)+1000;
function store(){
 const files=new Map<string,Buffer>();let writes=0;
 return {files,get writes(){return writes;},read:async(path:string)=>{const body=files.get(path);return body?{body,etag:hash(body)}:null;},
 write:async(path:string,body:Buffer,etag?:string)=>{writes++;const prior=files.get(path);if(etag? !prior||hash(prior)!==etag:!!prior)throw Error('conflict');files.set(path,body);}};
}

test('real partition publication reuses immutable files and is idempotent',async()=>{
 const s=store();const first=await publishWeatherPartitions(input,s,null,now);
 assert.equal(first.uploaded,input.objects.size);
 const count=s.writes;
 const repeated=await publishWeatherPartitions(input,s,input.publication.sha256,now);
 assert.equal(repeated.uploaded,0);assert.equal(repeated.reused,input.objects.size);assert.equal(s.writes,count);
 assert.equal((await readWeatherPartitionPointer(s,now))?.publication.sha256,input.publication.sha256);
});

test('failed upload leaves pointer absent and lost write responses require exact readback',async()=>{
 const failed=store();
 await assert.rejects(publishWeatherPartitions(input,{...failed,write:async()=>{throw Error('offline');}},null,now),/offline/);
 assert.equal(failed.files.has(WEATHER_PARTITION_POINTER),false);
 const uncertain=store();
 await publishWeatherPartitions(input,{...uncertain,write:async(...args)=>{await uncertain.write(...args);throw Error('lost response');}},null,now);
 assert.ok(uncertain.files.has(WEATHER_PARTITION_POINTER));
});

test('a competing publisher is preserved when the final pointer cannot be acquired',async()=>{
 const s=store(),winner=Buffer.from('competing publication');
 await assert.rejects(publishWeatherPartitions(input,{...s,write:async(path,body,etag)=>{
  if(path===WEATHER_PARTITION_POINTER)s.files.set(path,winner);
  await s.write(path,body,etag);
 }},null,now),/conflict/);
 assert.deepEqual(s.files.get(WEATHER_PARTITION_POINTER),winner);
});

test('missing referenced indexes or sources fail before any storage mutation',async()=>{
 const root=JSON.parse(input.objects.get(input.publication.sha256)!.toString());
 const index=JSON.parse(input.objects.get(root.index.sha256)!.toString());
 const partition=JSON.parse(input.objects.get((Object.values(index.games)[0] as any).sha256)!.toString());
 for(const identity of [root.index.sha256,(Object.values(partition.sources)[0] as any).sha256]){
  const s=store(),objects=new Map(input.objects);objects.delete(identity);
  await assert.rejects(publishWeatherPartitions({...input,objects},s,null,now),/integrity|missing/);
  assert.equal(s.writes,0);
 }
});

test('current snapshot anchors must exist in the proposed history index',async()=>{
 const objects=new Map(input.objects),root=JSON.parse(objects.get(input.publication.sha256)!.toString());
 const index=JSON.parse(objects.get(root.index.sha256)!.toString());index.games={};
 function retain(value:unknown){const body=Buffer.from(JSON.stringify(value)),sha256=hash(body);objects.set(sha256,body);return {sha256,bytes:body.length};}
 root.index=retain(index);const publication=retain(root),s=store();
 await assert.rejects(publishWeatherPartitions({publication,objects},s,null,now),/missing from history index/);
 assert.equal(s.writes,0);
});
