import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {prepareWeatherPublication} from '../scripts/weather_publication_inputs';
test('real publisher inputs bind canonical ledger and retained source objects',()=>{
 const result=prepareWeatherPublication(process.cwd());
 const fingerprint=(b:Buffer)=>createHash('sha256').update(b).digest('hex');
 assert.equal(fingerprint(result.objects[1]),result.bundle.ledgerSha256);
 assert.equal(result.objects.length,result.bundle.sourceHashes.length+2);
 result.bundle.sourceHashes.forEach((hash,index)=>assert.equal(fingerprint(gunzipSync(result.objects[index+2])),hash));
});
