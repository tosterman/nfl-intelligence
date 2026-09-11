import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readWeatherStream, weatherBlobPath} from '../src/lib/weather-blob';
test('bounded weather reads cancel streams that exceed declared size',async()=>{
 let cancelled=false;
 const stream=new ReadableStream<Uint8Array>({start(c){c.enqueue(Buffer.from('too large'));},cancel(){cancelled=true;}});
 await assert.rejects(readWeatherStream(stream,3),/size/);
 assert.equal(cancelled,true);
 const valid=new ReadableStream<Uint8Array>({start(c){c.enqueue(Buffer.from('abc'));c.close();}});
 assert.equal((await readWeatherStream(valid,3)).toString(),'abc');
});
test('weather storage paths cannot target odds or arbitrary objects',()=>{
 for(const path of ['weather/latest.json',`weather/objects/${'a'.repeat(64)}`,`weather/manifests/${'b'.repeat(64)}.json`])assert.equal(weatherBlobPath(path),path);
 for(const path of ['odds/latest.json','weather/../odds/latest.json','https://example.com','weather/objects/not-a-hash'])assert.throws(()=>weatherBlobPath(path));
});
