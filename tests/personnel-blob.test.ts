import {test} from 'node:test';
import assert from 'node:assert/strict';
import {personnelBlobPath} from '../src/lib/personnel-blob';

test('personnel storage permits only its pointer and immutable object namespace',()=>{
  for(const path of ['personnel/latest.json',`personnel/objects/${'a'.repeat(64)}`])assert.equal(personnelBlobPath(path),path);
  for(const path of ['weather/latest.json','personnel/../latest.json','personnel/objects/.env','personnel/latest-v2.json'])assert.throws(()=>personnelBlobPath(path));
});
