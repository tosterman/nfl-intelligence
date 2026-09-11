import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {freezeLegacyWeather} from '../src/lib/weather-migration-freeze';
import {publishWeatherObjects,readWeatherObjects} from '../src/lib/weather-publication';
const hash=(b:Buffer)=>createHash('sha256').update(b).digest('hex');
function store(){const files=new Map<string,Buffer>();return {files,
 read:async(path:string)=>{const body=files.get(path);return body?{body,etag:hash(body)}:null;},
 write:async(path:string,body:Buffer,etag?:string)=>{const old=files.get(path);if(etag?!old||hash(old)!==etag:!!old)throw Error('conflict');files.set(path,body);}};}

test('freeze keeps legacy data readable while preventing subsequent v1 publication',async()=>{
 const s=store(),body=Buffer.from('retained history');
 const manifest=await publishWeatherObjects([body],'2026-09-11T12:00:00Z',s);
 await freezeLegacyWeather(s,manifest);await freezeLegacyWeather(s,manifest);
 assert.deepEqual((await readWeatherObjects(s))?.objects,[body]);
 await assert.rejects(publishWeatherObjects([Buffer.from('new')],'2026-09-11T13:00:00Z',s),/frozen/);
});

test('freeze invalidates the ETag held by an in-flight v1 publisher',async()=>{
 const s=store(),manifest=await publishWeatherObjects([Buffer.from('first')],'2026-09-11T12:00:00Z',s);
 await assert.rejects(publishWeatherObjects([Buffer.from('second')],'2026-09-11T13:00:00Z',{...s,write:async(path,body,etag)=>{
  if(path==='weather/latest.json')await freezeLegacyWeather(s,manifest);
  await s.write(path,body,etag);
 }}),/conflict/);
 assert.equal((await readWeatherObjects(s))?.manifestHash,manifest);
});

test('lost freeze response requires exact readback and changed legacy identity is rejected',async()=>{
 const s=store(),manifest=await publishWeatherObjects([Buffer.from('first')],'2026-09-11T12:00:00Z',s);
 await assert.rejects(freezeLegacyWeather(s,'f'.repeat(64)),/changed/);
 await freezeLegacyWeather({...s,write:async(...args)=>{await s.write(...args);throw Error('lost');}},manifest);
 assert.equal((await readWeatherObjects(s))?.frozenForMigration,true);
});
