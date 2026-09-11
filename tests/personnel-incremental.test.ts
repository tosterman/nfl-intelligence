import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {gzipSync} from 'node:zlib';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {staticPersonnelEvidence} from '../src/lib/personnel-static';
import {site} from '../src/lib/data';
import {preparePersonnelIncremental} from '../scripts/personnel_incremental_inputs';

test('incremental package binds accepted capture and pinned inputs before publication',async()=>{
  const directory=await mkdtemp(join(tmpdir(),'nfl-incremental-'));
  try{
    const objects=new Map<string,Buffer>();
    const retain=(body:Buffer)=>{const sha256=createHash('sha256').update(body).digest('hex');objects.set(sha256,body);return {sha256,bytes:body.length};};
    const encode=(v:unknown)=>retain(Buffer.from(JSON.stringify(v)));
    const snapshot=Buffer.from(JSON.stringify(staticPersonnelEvidence.snapshot));
    const capture=createHash('sha256').update(snapshot).digest('hex');
    const path=`data/personnel-sources/${capture}.snapshot.json.gz`;
    const archive:Record<string,{sha256:string;bytes:number}>={[path]:retain(gzipSync(snapshot))};
    archive['data/personnel.json']=retain(snapshot);
    archive['data/personnel-changes.json']=encode(staticPersonnelEvidence.history);
    for(const name of ['data/site.json','data/games.csv','reviews/player-registry-source.json',
      'reviews/player-identity-source.csv.gz','reviews/player-usage-source.csv.gz'])archive[name]=retain(Buffer.from(name));
    const generatedAt=new Date(Date.now()-1000).toISOString(),g=site.games[0];
    const context=Object.fromEntries(['id','season','week','type','home','away','kickoff','venue','neutral'].map(k=>[k,g[k as keyof typeof g]]));
    const presentation=encode({schemaVersion:1,kind:'personnel-presentation',generatedAt,scheduleHash:site.source.sha256,
      contexts:{[g.id]:context},evidence:staticPersonnelEvidence,derivation:{status:'compatible',cutoff:staticPersonnelEvidence.snapshot.retrievedAt,reason:null}});
    const prior=encode({schemaVersion:1,kind:'personnel-publication',generatedAt,presentation,archive,previous:null});
    const pointer=Buffer.from(JSON.stringify({schemaVersion:1,generatedAt,publication:prior}));
    const store={read:async(name:string)=>{const body=name==='personnel/latest.json'?pointer:objects.get(name.split('/').at(-1)!);return body?{body,etag:'test'}:null;}};
    async function prepare(change:'none'|'pin'|'capture'|'previous'|'history'){
      const proof=encode({mode:'recurring',previousPublication:prior,previousCapture:change==='capture'?'a'.repeat(64):capture,
        transitionReplayed:true,inputsUnchanged:true});
      const nextArchive:typeof archive={...archive,'reviews/personnel-replay-proof.json':proof};
      if(change==='pin')nextArchive['data/games.csv']=retain(Buffer.from('changed'));
      if(change==='history')nextArchive['data/personnel-changes.json']=encode({...staticPersonnelEvidence.history,previousRetrievedAt:'2000-01-01T00:00:00Z'});
      const publication=encode({schemaVersion:1,kind:'personnel-publication',generatedAt,presentation,archive:nextArchive,
        previous:change==='previous'?null:prior});
      for(const [id,body]of objects)await writeFile(join(directory,id),body);
      await writeFile(join(directory,'candidate.json'),JSON.stringify({publication,objects:[...objects.keys()],objectCount:objects.size,
        bytes:[...objects.values()].reduce((n,b)=>n+b.length,0)}));
      return preparePersonnelIncremental(directory,store);
    }
    assert.equal((await prepare('none')).previous,prior.sha256);
    await assert.rejects(prepare('pin'),/Pinned/);
    await assert.rejects(prepare('capture'),/capture/);
    await assert.rejects(prepare('previous'),/predecessor/);
    await assert.rejects(prepare('history'),/preserve accepted history/);
  }finally{await rm(directory,{recursive:true,force:true});}
});
