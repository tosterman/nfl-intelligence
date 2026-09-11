import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readWeatherPartitionRoot,readWeatherGamePartition,readWeatherPartitionSnapshot} from '../src/lib/weather-partition-store';
import {boundWeatherRecord} from '../src/lib/weather-bundle';
import venues from '../data/weather-venues.json';
import extraVenues from '../data/weather-osm-venues.json';

const fixture=JSON.parse(execFileSync('python',['-c',"import sys,json,base64;sys.path.insert(0,'scripts');from weather_partitions import build_partitions;r=build_partitions();print(json.dumps({'publication':r['publication'],'objects':{h:base64.b64encode(b).decode() for h,b in r['objects'].items()}}))"],{maxBuffer:10_000_000}).toString());
const fixtureNow=Date.parse(JSON.parse(Buffer.from(fixture.objects[fixture.publication.sha256],'base64').toString()).generatedAt)+1000;
function store(){
 const files=new Map<string,Buffer>(Object.entries(fixture.objects).map(([hash,value])=>['weather/objects/'+hash,Buffer.from(value as string,'base64')]));
 const reads:string[]=[];
 return {files,reads,read:async(path:string)=>{reads.push(path);const body=files.get(path);return body?{body,etag:'fixture'}:null;}};
}

test('real migrated archive supports scoped snapshot and per-game reads without source downloads',async()=>{
 const s=store();
 const root=await readWeatherPartitionRoot(s,fixture.publication,fixtureNow);
 const snapshot=await readWeatherPartitionSnapshot(s,root,fixtureNow);
 const available=Object.entries(snapshot.weather.games).filter(([,row])=>row.status==='available');
 assert.equal(snapshot.history.records.length,available.length);
 const [id]=available[0];
 assert.ok(boundWeatherRecord(snapshot,snapshot.contexts[id],{...venues,...extraVenues}));
 assert.equal(boundWeatherRecord(snapshot,{...snapshot.contexts[id],neutral:true},{...venues,...extraVenues}),undefined);
 assert.equal(s.reads.length,2);
 const history=await readWeatherGamePartition(s,root,'2026_01_ATL_PIT');
 assert.ok(history);assert.equal(history.gameId,'2026_01_ATL_PIT');
 assert.ok(history.history.records.length>0);
 assert.equal(s.reads.length,4); // Root, snapshot, index, selected partition only.
 const absent=await readWeatherGamePartition(s,root,'2026_01_NO_SUCH_GAME');
 assert.equal(absent,null);
});

test('rehashed snapshots still require retained current evidence and matching collection context',async()=>{
 for(const mutate of [
  (p:any)=>{p.history.records=[];},
  (p:any)=>{const id=Object.keys(p.weather.games).find(id=>p.weather.games[id].status==='available')!;p.contexts[id].neutral=true;},
  (p:any)=>{const id=Object.keys(p.weather.games).find(id=>p.weather.games[id].status==='available')!;p.weather.games[id].retrievedAt='2000-01-01T00:00:00Z';},
 ]){
  const s=store(),root=await readWeatherPartitionRoot(s,fixture.publication,fixtureNow);
  const snapshot=JSON.parse(s.files.get('weather/objects/'+root.snapshot.sha256)!.toString());
  const envelope=JSON.parse(snapshot.bundleJson),payload=JSON.parse(envelope.payloadJson);
  mutate(payload);envelope.payloadJson=JSON.stringify(payload);
  envelope.manifest.payloadSha256=createHash('sha256').update(envelope.payloadJson).digest('hex');
  envelope.manifest.payloadBytes=Buffer.byteLength(envelope.payloadJson);
  snapshot.bundleJson=JSON.stringify(envelope);
  const raw=Buffer.from(JSON.stringify(snapshot)),sha256=createHash('sha256').update(raw).digest('hex');
  s.files.set('weather/objects/'+sha256,raw);
  await assert.rejects(readWeatherPartitionSnapshot(s,{...root,snapshot:{sha256,bytes:raw.length}},fixtureNow),/weather|Weather/);
 }
});

test('missing or corrupted referenced objects and future publication fail closed',async()=>{
 const s=store();const path='weather/objects/'+fixture.publication.sha256;
 s.files.set(path,Buffer.from('{}'));
 await assert.rejects(readWeatherPartitionRoot(s,fixture.publication),/integrity/);
 s.files.delete(path);
 await assert.rejects(readWeatherPartitionRoot(s,fixture.publication),/integrity/);
 await assert.rejects(readWeatherPartitionRoot(store(),fixture.publication,0),/time/);
});

test('hash-valid index aliases cannot substitute another game partition',async()=>{
 const s=store();const root=await readWeatherPartitionRoot(s,fixture.publication,fixtureNow);
 const index=JSON.parse(s.files.get('weather/objects/'+root.index.sha256)!.toString());
 const ids=Object.keys(index.games);index.games[ids[0]]=index.games[ids[1]];
 const raw=Buffer.from(JSON.stringify(index)),hash=createHash('sha256').update(raw).digest('hex');
 s.files.set('weather/objects/'+hash,raw);
 await assert.rejects(readWeatherGamePartition(s,{...root,index:{sha256:hash,bytes:raw.length}},ids[0]),/game/);
});

test('rehashing cannot hide inconsistent compact history or missing source references',async()=>{
 for(const mutate of [
  (p:any)=>{p.history.records[0].temperature=999;},
  (p:any)=>{p.sources={};},
  (p:any)=>{p.history.records[1]={...p.history.records[0]};},
 ]){
  const s=store(),root=await readWeatherPartitionRoot(s,fixture.publication,fixtureNow);
  const index=JSON.parse(s.files.get('weather/objects/'+root.index.sha256)!.toString());
  const game=Object.keys(index.games)[0];
  const partition=JSON.parse(s.files.get('weather/objects/'+index.games[game].sha256)!.toString());
  mutate(partition);
  function retain(value:unknown){const raw=Buffer.from(JSON.stringify(value)),sha256=createHash('sha256').update(raw).digest('hex');s.files.set('weather/objects/'+sha256,raw);return {sha256,bytes:raw.length};}
  index.games[game]=retain(partition);
  await assert.rejects(readWeatherGamePartition(s,{...root,index:retain(index)},game),/history|observation/);
 }
});
