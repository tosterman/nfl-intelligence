import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {join,relative} from 'node:path';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {staticPersonnelEvidence} from '../src/lib/personnel-static';
import {site} from '../src/lib/data';
import {restorePersonnelInputs} from '../scripts/personnel_restore';

function fixture(){
  const objects=new Map<string,Buffer>(),archive:Record<string,{sha256:string;bytes:number}>={};
  const retain=(body:Buffer)=>{const sha256=createHash('sha256').update(body).digest('hex');objects.set(sha256,body);return {sha256,bytes:body.length};};
  const root=process.cwd();
  for(const directory of ['data','reviews'])for(const entry of readdirSync(join(root,directory),{recursive:true,withFileTypes:true})){
    if(!entry.isFile())continue;
    const path=join(entry.parentPath,entry.name),name=relative(root,path).replaceAll('\\','/');
    if(!/\.(json|csv|gz)$/.test(name))continue;
    // Only inputs needed by this fixture, not unrelated numerical archives.
    if(directory==='data'&&name.includes('/')&&name.slice(5).includes('/')&&!/^data\/(personnel|quarterback|participation)-sources\//.test(name))continue;
    if(directory==='reviews'&&!/^reviews\/(player-|personnel-identity-audit)/.test(name))continue;
    archive[name]=retain(readFileSync(path));
  }
  archive['data/games.csv']=retain(gunzipSync(readFileSync(`data/forecast-input-archive/objects/${site.source.sha256}.gz`)));
  archive['scripts/unused.py']=retain(Buffer.from('# retained code\n'));
  const generatedAt=new Date(Date.now()-1000).toISOString();
  const contexts=Object.fromEntries(site.games.map(g=>[g.id,Object.fromEntries(['id','season','week','type','home','away','kickoff','venue','neutral'].map(k=>[k,g[k as keyof typeof g]]))]));
  const presentation=retain(Buffer.from(JSON.stringify({schemaVersion:1,kind:'personnel-presentation',generatedAt,
    scheduleHash:site.source.sha256,contexts,evidence:staticPersonnelEvidence,
    derivation:{status:'compatible',cutoff:staticPersonnelEvidence.snapshot.retrievedAt,reason:null}})));
  const publication=retain(Buffer.from(JSON.stringify({schemaVersion:1,kind:'personnel-publication',generatedAt,presentation,archive,previous:null})));
  const pointer=Buffer.from(JSON.stringify({schemaVersion:1,generatedAt,publication}));
  const reads:string[]=[];
  return {objects,archive,reads,store:{read:async(path:string)=>{
    reads.push(path);const body=path==='personnel/latest.json'?pointer:objects.get(path.split('/').at(-1)!);
    return body?{body,etag:'fixture'}:null;
  }}};
}

test('recurring restore selects only current captures and reconstructs source closure',async()=>{
  const f=fixture(),result=await restorePersonnelInputs(f.store);
  assert.equal([...result.files.keys()].filter(n=>n.startsWith('data/personnel-sources/')&&n.endsWith('.snapshot.json.gz')).length,1);
  assert.equal([...result.files.keys()].filter(n=>n.startsWith('data/quarterback-sources/')&&n.endsWith('.snapshot.json.gz')).length,1);
  assert.equal(result.files.has('reviews/personnel-change-ledger.json'),false);
  assert.ok(result.files.has('data/games.csv'));
  const selected=new Set([...result.files.keys()].map(n=>f.archive[n].sha256));
  const unrelated=Object.entries(f.archive).find(([name,ref])=>name.startsWith('data/personnel-sources/')&&!selected.has(ref.sha256));
  assert.ok(unrelated);assert.ok(!f.reads.includes('personnel/objects/'+unrelated[1].sha256));
});

test('missing or corrupt selected inputs reject restore',async()=>{
  for(const corrupt of [false,true]){
    const f=fixture(),id=f.archive['data/personnel.json'].sha256;
    if(corrupt)f.objects.set(id,Buffer.from('{}'));else f.objects.delete(id);
    await assert.rejects(restorePersonnelInputs(f.store),/integrity failure/);
  }
});
