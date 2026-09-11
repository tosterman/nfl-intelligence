import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,dirname,resolve} from 'node:path';
import {prepareWeatherPublication} from '../scripts/weather_publication_inputs';
import {restoreWeatherArchive} from '../scripts/weather_restore';
test('published history restores into a fresh worker and conflicting local evidence is preserved',()=>{
 const input=prepareWeatherPublication(process.cwd());const root=mkdtempSync(join(tmpdir(),'nfl-weather-'));
 try{
  restoreWeatherArchive(root,input.objects);
  const path=join(root,'data/weather-ledger.json'),before=readFileSync(path);
  assert.ok(JSON.parse(before.toString()).length>0);
  restoreWeatherArchive(root,input.objects);assert.deepEqual(readFileSync(path),before);
  const changed=JSON.parse(before.toString());changed[0].temperature=999;writeFileSync(path,JSON.stringify(changed));
  const conflict=readFileSync(path);assert.throws(()=>restoreWeatherArchive(root,input.objects),/conflict/);
  assert.deepEqual(readFileSync(path),conflict);
 }finally{assert.equal(dirname(resolve(root)),resolve(tmpdir()));rmSync(root,{recursive:true,force:true});}
});
