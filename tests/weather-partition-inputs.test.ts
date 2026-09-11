import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {prepareWeatherPartitionCandidate} from '../scripts/weather_partition_inputs';
import {prepareWeatherPublication} from '../scripts/weather_publication_inputs';
import {publishWeatherObjects} from '../src/lib/weather-publication';
import {publishWeatherPartitions} from '../src/lib/weather-partition-publication';
const hash=(b:Buffer)=>createHash('sha256').update(b).digest('hex');
function store(){
 const files=new Map<string,Buffer>();
 return {files,read:async(path:string)=>{const body=files.get(path);return body?{body,etag:hash(body)}:null;},
 write:async(path:string,body:Buffer,etag?:string)=>{const old=files.get(path);if(etag? !old||hash(old)!==etag:!!old)throw Error('conflict');files.set(path,body);}};
}

test('candidate preparation requires published legacy evidence and supports subsequent v2 continuity',async()=>{
 const s=store();
 await assert.rejects(prepareWeatherPartitionCandidate(process.cwd(),s),/bootstrap history/);
 const legacy=prepareWeatherPublication(process.cwd());
 const manifest=await publishWeatherObjects(legacy.objects,legacy.bundle.weather.generatedAt,s,null);
 const first=await prepareWeatherPartitionCandidate(process.cwd(),s);
 assert.equal(first.legacyManifestHash,manifest);assert.equal(first.previous,null);
 assert.equal(first.summary.observations,legacy.bundle.history.records.length);
 await publishWeatherPartitions(first.candidate,s,null);
 const next=await prepareWeatherPartitionCandidate(process.cwd(),s);
 assert.equal(next.previous,first.candidate.publication.sha256);assert.equal(next.legacyManifestHash,null);
 assert.deepEqual(next.candidate.publication,first.candidate.publication);
});

test('preserving the same legacy ledger cannot justify an older current snapshot',async()=>{
 const s=store(),legacy=prepareWeatherPublication(process.cwd());
 const envelope=JSON.parse(legacy.objects[0].toString()),payload=JSON.parse(envelope.payloadJson);
 const later=new Date(Date.parse(payload.weather.generatedAt)+60000).toISOString();
 payload.weather.generatedAt=later;envelope.manifest.generatedAt=later;
 envelope.payloadJson=JSON.stringify(payload);envelope.manifest.payloadBytes=Buffer.byteLength(envelope.payloadJson);
 envelope.manifest.payloadSha256=hash(Buffer.from(envelope.payloadJson));
 await publishWeatherObjects([Buffer.from(JSON.stringify(envelope)),...legacy.objects.slice(1)],later,s,null);
 await assert.rejects(prepareWeatherPartitionCandidate(process.cwd(),s),/older than published legacy/);
});
