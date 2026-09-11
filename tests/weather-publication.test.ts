import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {publishWeatherObjects, readWeatherObjects} from '../src/lib/weather-publication';
const hash=(b:Buffer)=>createHash('sha256').update(b).digest('hex');
function store(){
 const files=new Map<string,Buffer>();
 return {files,read:async(path:string)=>{const body=files.get(path);return body?{body,etag:hash(body)}:null;},
 write:async(path:string,body:Buffer,etag?:string)=>{const old=files.get(path);if(etag? !old||hash(old)!==etag:!!old)throw Error('conflict');files.set(path,body);}};
}
test('weather pointer only advances after every immutable object is verified',async()=>{
 const s=store();const body=Buffer.from('verified fixture');
 await publishWeatherObjects([body],'2026-09-11T12:00:00Z',s);
 const prior=s.files.get('weather/latest.json');assert.ok(prior);
 await assert.rejects(publishWeatherObjects([Buffer.from('new')],'2026-09-11T13:00:00Z',{...s,write:async()=>{throw Error('upload failed');}}));
 assert.deepEqual(s.files.get('weather/latest.json'),prior);
 await assert.rejects(publishWeatherObjects([body],'2026-09-11T11:00:00Z',s),/older/);
 await publishWeatherObjects([body],'2026-09-11T12:00:00Z',s);
 assert.deepEqual(s.files.get('weather/latest.json'),prior);
});
test('lost immutable write response is recovered by exact bytes; corrupted readback fails',async()=>{
 const s=store();let lost=true;
 await publishWeatherObjects([Buffer.from('fixture')],'2026-09-11T12:00:00Z',{...s,write:async(...args)=>{await s.write(...args);if(lost){lost=false;throw Error('lost response');}}});
 const bad=store();
 await assert.rejects(publishWeatherObjects([Buffer.from('fixture')],'2026-09-11T12:00:00Z',{...bad,read:async(path)=>path.startsWith('weather/objects/')?{body:Buffer.from('wrong'),etag:'wrong'}:bad.read(path)}),/readback/);
 assert.ok(!bad.files.has('weather/latest.json'));
});
test('concurrent pointer changes and conflicting same-time collections cannot overwrite',async()=>{
 const s=store();await publishWeatherObjects([Buffer.from('first')],'2026-09-11T12:00:00Z',s);
 await assert.rejects(publishWeatherObjects([Buffer.from('different')],'2026-09-11T12:00:00Z',s),/Conflicting/);
 const winner=Buffer.from(JSON.stringify({schemaVersion:1,generatedAt:'2026-09-11T14:00:00Z',manifestHash:'a'.repeat(64)}));
 await assert.rejects(publishWeatherObjects([Buffer.from('second')],'2026-09-11T13:00:00Z',{...s,write:async(path,body,etag)=>{
   if(path==='weather/latest.json')s.files.set(path,winner);
   await s.write(path,body,etag);
 }}),/conflict/);
 assert.deepEqual(s.files.get('weather/latest.json'),winner);
});
test('lost pointer response is accepted only with exact committed readback',async()=>{
 const s=store();await publishWeatherObjects([Buffer.from('first')],'2026-09-11T12:00:00Z',{...s,write:async(path,body,etag)=>{
   await s.write(path,body,etag);if(path==='weather/latest.json')throw Error('response lost');
 }});
 assert.ok(s.files.has('weather/latest.json'));
});
test('reader verifies complete hash chain and may select presentation without source downloads',async()=>{
 const s=store();const objects=[Buffer.from('presentation'),Buffer.from('source')];
 assert.equal(await readWeatherObjects(s),null);
 await publishWeatherObjects(objects,'2026-09-11T12:00:00Z',s);
 const calls:string[]=[];
 const result=await readWeatherObjects({...s,read:async(path)=>{calls.push(path);return s.read(path);}},[0]);
 assert.deepEqual(result!.objects,[objects[0]]);
 assert.ok(!calls.includes(`weather/objects/${hash(objects[1])}`));
 s.files.set(`weather/objects/${hash(objects[0])}`,Buffer.from('corrupt'));
 await assert.rejects(readWeatherObjects(s),/integrity/);
});
test('reader rejects missing manifests, oversized declarations and timestamp disagreement',async()=>{
 const s=store();await publishWeatherObjects([Buffer.from('value')],'2026-09-11T12:00:00Z',s);
 const pointer=JSON.parse(s.files.get('weather/latest.json')!.toString());
 const path=`weather/manifests/${pointer.manifestHash}.json`;
 const original=s.files.get(path)!;s.files.delete(path);
 await assert.rejects(readWeatherObjects(s),/manifest/);
 for(const change of [{generatedAt:'2026-09-12T12:00:00Z'},{objects:[{sha256:'a'.repeat(64),bytes:20_000_001}]}]){
  const body=Buffer.from(JSON.stringify({...JSON.parse(original.toString()),...change}));
  s.files.set(`weather/manifests/${hash(body)}.json`,body);
  s.files.set('weather/latest.json',Buffer.from(JSON.stringify({...pointer,manifestHash:hash(body)})));
  await assert.rejects(readWeatherObjects(s),/manifest/);
 }
});
test('publication rejects a pointer changed since weather history validation',async()=>{
 const s=store();const old=await publishWeatherObjects([Buffer.from('old')],'2026-09-11T12:00:00Z',s);
 await publishWeatherObjects([Buffer.from('newer')],'2026-09-11T13:00:00Z',s);
 const current=s.files.get('weather/latest.json');
 await assert.rejects(publishWeatherObjects([Buffer.from('based on old')],'2026-09-11T14:00:00Z',s,old),/validation/);
 assert.deepEqual(s.files.get('weather/latest.json'),current);
 await assert.rejects(publishWeatherObjects([Buffer.from('first')],'2026-09-11T14:00:00Z',s,null),/validation/);
});
