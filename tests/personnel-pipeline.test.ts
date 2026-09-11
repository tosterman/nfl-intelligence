import {test} from 'node:test';
import assert from 'node:assert/strict';
import {personnelPipeline} from '../scripts/personnel_pipeline';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {mkdtemp,mkdir,writeFile,readFile,access,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {resolve,join,sep} from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

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

test('actual wrapper removes stale success and retains current failure without live services',async()=>{
  const parent=resolve(tmpdir()),directory=await mkdtemp(join(parent,'nfl-pipeline-failure-'));
  try{
    await mkdir(join(directory,'reviews'));
    const old='{"status":"completed","publication":"old-success"}';
    await writeFile(join(directory,'reviews/personnel-incremental-publication.json'),old);
    await writeFile(join(directory,'reviews/personnel-pipeline.json'),old);
    await writeFile(join(directory,'reviews/unrelated.json'),'preserved');
    const loader=createRequire(import.meta.url).resolve('tsx');
    // This empty workspace has no restore script or dependencies. The child
    // fails before any source or storage operation can execute.
    await assert.rejects(promisify(execFile)(process.execPath,['--import',pathToFileURL(loader).href,
      resolve('scripts/collect_personnel.ts'),'--publish'],{cwd:directory,timeout:30000,windowsHide:true}));
    const report=JSON.parse(await readFile(join(directory,'reviews/personnel-pipeline.json'),'utf8'));
    assert.equal(report.status,'failed');assert.equal(report.stages.length,1);
    assert.equal(report.stages[0].script,'scripts/restore_personnel_worker.ts');
    assert.equal(report.stages[0].status,'failed');
    assert.ok(Date.parse(report.finishedAt)>=Date.parse(report.startedAt));
    await assert.rejects(access(join(directory,'reviews/personnel-incremental-publication.json')));
    await assert.rejects(access(join(directory,'release-recovery/personnel-worker.lock')));
    assert.equal(await readFile(join(directory,'reviews/unrelated.json'),'utf8'),'preserved');
    await writeFile(join(directory,'release-recovery/personnel-worker.lock'),'another-owner');
    await writeFile(join(directory,'reviews/personnel-pipeline.json'),old);
    await assert.rejects(promisify(execFile)(process.execPath,['--import',pathToFileURL(loader).href,
      resolve('scripts/collect_personnel.ts')],{cwd:directory,timeout:30000,windowsHide:true}));
    assert.equal(await readFile(join(directory,'release-recovery/personnel-worker.lock'),'utf8'),'another-owner');
    assert.equal(await readFile(join(directory,'reviews/personnel-pipeline.json'),'utf8'),old);
  }finally{
    assert.ok(resolve(directory).startsWith(parent+sep+'nfl-pipeline-failure-'));
    await rm(directory,{recursive:true,force:true});
  }
});
