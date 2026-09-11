import {writeFile} from 'node:fs/promises';
import {loadPersonnelBootstrap} from './personnel_bootstrap_inputs';
import {personnelBlobStore} from '../src/lib/personnel-blob';
import {publishPersonnelObjects,type PersonnelObjectStore} from '../src/lib/personnel-publication';

async function main(){
  const [directory,mode,...extra]=process.argv.slice(2);
  if(!directory||(mode!==undefined&&mode!=='--publish')||extra.length)
    throw Error('Usage: publish_personnel_bootstrap.ts package-directory [--publish]');
  const input=await loadPersonnelBootstrap(directory);
  // Exercise the complete transaction before any external write.
  const memory=new Map<string,{body:Buffer;etag:string}>();
  const rehearsal:PersonnelObjectStore={read:async path=>memory.get(path)??null,
    write:async(path,body,etag)=>{
      if(memory.get(path)?.etag!==etag)throw Error('Rehearsal publication conflict');
      memory.set(path,{body,etag:String(memory.size+1)});
    }};
  await publishPersonnelObjects(input,rehearsal,null);
  const result=mode==='--publish'?await publishPersonnelObjects(input,personnelBlobStore,null):null;
  const report={checkedAt:new Date().toISOString(),mode:mode==='--publish'?'published':'local-rehearsal',
    publication:input.publication,objectCount:input.objects.size,result,
    scope:'Private storage bootstrap; public page availability and scheduled collection are separate checks'};
  await writeFile('reviews/personnel-bootstrap-publication.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
}
main().catch(error=>{
  let detail=error instanceof Error?error.message:'Unknown failure';
  for(const [key,value]of Object.entries(process.env))if(value&&/token|secret|password|key/i.test(key))detail=detail.split(value).join('[redacted]');
  console.error('Personnel bootstrap failed:',detail.slice(0,1000));process.exitCode=1;
});
