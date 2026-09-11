import {test} from 'node:test';
import assert from 'node:assert/strict';
import {personnelPipeline} from '../scripts/personnel_pipeline';

test('pipeline binds restored predecessor and stops before publication on failed replay',async()=>{
  const publication={sha256:'a'.repeat(64),bytes:100},capture='b'.repeat(64);
  const restored={publication,capture,directory:'release-recovery/restored'};
  const refreshed={previousPublication:publication,previousCapture:capture,directory:'release-recovery/refreshed'};
  const calls:string[][]=[];
  await assert.rejects(personnelPipeline(async(_,args)=>{
    calls.push(args);
    if(calls.length===1)return restored;
    if(calls.length===2)return refreshed;
    throw Error('Replay failed');
  },true),/Replay failed/);
  assert.equal(calls.length,3);
  assert.ok(calls.every(args=>!args.includes('--publish')));
  await assert.rejects(personnelPipeline(async()=>({...restored,directory:'../elsewhere'})),/outside/);
  let count=0;
  await assert.rejects(personnelPipeline(async()=>++count===1?restored:{...refreshed,previousCapture:'c'.repeat(64)}),/selected restoration/);
});
