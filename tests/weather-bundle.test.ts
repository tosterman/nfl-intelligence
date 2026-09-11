import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {decodeWeatherBundle, assertWeatherContinuity, boundWeatherRecord} from '../src/lib/weather-bundle';
import {readFileSync} from 'node:fs';

test('Python weather transport verifies exact payload bytes in JavaScript',()=>{
 const raw=execFileSync('python',['-c',"import sys;sys.path.insert(0,'scripts');from weather_bundle import build,transport;sys.stdout.buffer.write(transport(build()))"],{maxBuffer:2_000_000});
 const now=Date.parse(JSON.parse(raw.toString()).manifest.generatedAt)+1000;
 const value=decodeWeatherBundle(raw,now);
 assert.ok(value.history.records.length>0);
 const altered=JSON.parse(raw.toString());altered.payloadJson+=' ';
 assert.throws(()=>decodeWeatherBundle(Buffer.from(JSON.stringify(altered))),/payload/);
 assert.throws(()=>decodeWeatherBundle(raw,0),/time/);
 assertWeatherContinuity(value,value);
 const removed=structuredClone(value);removed.history.records.shift();
 assert.throws(()=>assertWeatherContinuity(value,removed),/history/);
 const changed=structuredClone(value);changed.history.records[0].temperature=999;
 assert.throws(()=>assertWeatherContinuity(value,changed),/history/);
 const venues={...JSON.parse(readFileSync('data/weather-venues.json','utf8')),...JSON.parse(readFileSync('data/weather-osm-venues.json','utf8'))};
 const id=Object.keys(value.weather.games).find(k=>value.weather.games[k].status==='available')!;
 const game=value.contexts[id];
 assert.equal(boundWeatherRecord(value,game,venues)?.status,'available');
 assert.equal(boundWeatherRecord(value,{...game,kickoff:'2027-01-01T00:00:00Z'},venues),undefined);
 assert.equal(boundWeatherRecord(value,{...game,neutral:true},venues),undefined);
 const moved=structuredClone(venues);moved[game.venue].latitude+=.01;
 assert.equal(boundWeatherRecord(value,game,moved),undefined);
 for(const kind of ['history','neutral','sources']){
  const changed=JSON.parse(raw.toString()),payload=JSON.parse(changed.payloadJson);
  const id=Object.keys(payload.weather.games).find(k=>payload.weather.games[k].status==='available')!;
  if(kind==='history')payload.history.records=[];
  if(kind==='neutral')payload.contexts[id].neutral=true;
  if(kind==='sources')changed.manifest.sourceHashes=[];
  changed.payloadJson=JSON.stringify(payload);
  changed.manifest.payloadBytes=Buffer.byteLength(changed.payloadJson);
  changed.manifest.payloadSha256=createHash('sha256').update(changed.payloadJson).digest('hex');
  assert.throws(()=>decodeWeatherBundle(Buffer.from(JSON.stringify(changed)),now),/history|references/,kind);
 }
});
