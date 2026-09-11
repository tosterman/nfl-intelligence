import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,mkdirSync,copyFileSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve,dirname} from 'node:path';
import {createHash} from 'node:crypto';
import {restoreWeatherPartitions} from '../scripts/weather_partition_restore';
import {prepareWeatherPartitionCandidate} from '../scripts/weather_partition_inputs';
import {publishWeatherPartitions,readWeatherPartitionPointer} from '../src/lib/weather-partition-publication';
import {readWeatherPartitionIndex} from '../src/lib/weather-partition-store';

test('one-game worker restores only its sources and preserves every other stored partition',async()=>{
 const raw=JSON.parse(execFileSync('python',['-c',"import sys,json,base64;sys.path.insert(0,'scripts');from weather_partitions import build_partitions;r=build_partitions();print(json.dumps({'publication':r['publication'],'objects':{h:base64.b64encode(b).decode() for h,b in r['objects'].items()}}))"],{maxBuffer:10_000_000}).toString());
 const input={publication:raw.publication,objects:new Map<string,Buffer>(Object.entries(raw.objects).map(([h,b])=>[h,Buffer.from(b as string,'base64')]))};
 const hash=(b:Buffer)=>createHash('sha256').update(b).digest('hex'),files=new Map<string,Buffer>();
 const store={read:async(path:string)=>{const body=files.get(path);return body?{body,etag:hash(body)}:null;},write:async(path:string,body:Buffer,etag?:string)=>{const old=files.get(path);if(etag?!old||hash(old)!==etag:!!old)throw Error('conflict');files.set(path,body);}};
 await publishWeatherPartitions(input,store,null);
 const previous=await readWeatherPartitionPointer(store);assert.ok(previous);
 const originalIndex=await readWeatherPartitionIndex(store,previous.root);
 const root=mkdtempSync(join(tmpdir(),'nfl-weather-scoped-'));
 try{
  mkdirSync(join(root,'data'));
  for(const name of ['site.json','weather.json','weather-venues.json','weather-osm-venues.json'])copyFileSync(join('data',name),join(root,'data',name));
  const selected='2026_01_ATL_PIT';
  const restored=await restoreWeatherPartitions(root,store,[selected]);
  assert.equal(restored.restoredGames,1);assert.ok(restored.observations>0&&restored.observations<JSON.parse(readFileSync('data/weather-ledger.json','utf8')).length);
  await assert.rejects(restoreWeatherPartitions(root,store,[selected]),/fresh worker ledger/);
  const weather=JSON.parse(readFileSync(join(root,'data/weather.json'),'utf8'));
  for(const [id,record] of Object.entries(weather.games) as [string,any][])if(id!==selected)weather.games[id]={status:'unavailable',gameId:id,kickoff:record.kickoff,venue:record.venue,reason:'Outside test worker scope'};
  weather.generatedAt=new Date(Date.parse(weather.generatedAt)+1000).toISOString();
  writeFileSync(join(root,'data/weather.json'),JSON.stringify(weather));
  execFileSync('python',['-c',"import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from weather_history import build;root=Path(sys.argv[2]);(root/'data/weather-history.json').write_text(json.dumps(build(root)))",resolve('scripts'),root]);
  const prepared=await prepareWeatherPartitionCandidate(root,store);
  await publishWeatherPartitions(prepared.candidate,store,prepared.previous);
  const next=await readWeatherPartitionPointer(store);assert.ok(next);
  assert.deepEqual(await readWeatherPartitionIndex(store,next.root),originalIndex);
 }finally{assert.equal(dirname(resolve(root)),resolve(tmpdir()));rmSync(root,{recursive:true,force:true});}
});
