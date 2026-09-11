import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {loadPersonnelBootstrap} from '../scripts/personnel_bootstrap_inputs';

test('bootstrap rejects traversal, duplicate inventory, changed bytes and noninitial roots',async()=>{
  const directory=await mkdtemp(join(tmpdir(),'nfl-personnel-inputs-'));
  try{
    const body=Buffer.from(JSON.stringify({previous:null}));
    const id=createHash('sha256').update(body).digest('hex');
    const manifest={objects:[id],objectCount:1,bytes:body.length,publication:{sha256:id,bytes:body.length}};
    const write=(value:unknown)=>writeFile(join(directory,'candidate.json'),JSON.stringify(value));
    await writeFile(join(directory,id),body);await write(manifest);
    assert.equal((await loadPersonnelBootstrap(directory)).objects.size,1);
    for(const bad of [{...manifest,objects:['../secret']},{...manifest,objects:[id,id],objectCount:2},
      {...manifest,bytes:body.length+1},{...manifest,objectCount:2}]){
      await write(bad);await assert.rejects(loadPersonnelBootstrap(directory));
    }
    await write(manifest);await writeFile(join(directory,id),'changed');
    await assert.rejects(loadPersonnelBootstrap(directory));
    const later=Buffer.from(JSON.stringify({previous:{sha256:id,bytes:body.length}}));
    const laterId=createHash('sha256').update(later).digest('hex');
    await writeFile(join(directory,laterId),later);
    await write({objects:[laterId],objectCount:1,bytes:later.length,publication:{sha256:laterId,bytes:later.length}});
    await assert.rejects(loadPersonnelBootstrap(directory),/initial publication/);
  }finally{await rm(directory,{recursive:true,force:true});}
});
