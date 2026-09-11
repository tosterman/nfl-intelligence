import {mkdir,mkdtemp,writeFile} from 'node:fs/promises';
import {resolve,join,relative,sep} from 'node:path';
import {personnelBlobStore} from '../src/lib/personnel-blob';
import {restorePersonnelInputs} from './personnel_restore';

async function main(){
  if(process.argv.length!==2)throw Error('Restore takes no arguments');
  const restored=await restorePersonnelInputs(personnelBlobStore);
  const parent=resolve('release-recovery');await mkdir(parent,{recursive:true});
  const directory=await mkdtemp(join(parent,'personnel-restored-'));
  for(const [name,raw]of restored.files){
    const path=resolve(directory,name);
    if(!path.startsWith(directory+sep))throw Error('Personnel restore path escapes workspace');
    await mkdir(resolve(path,'..'),{recursive:true});await writeFile(path,raw,{flag:'wx'});
  }
  const report={checkedAt:new Date().toISOString(),publication:restored.publication,capture:restored.capture,
    files:restored.files.size,bytes:restored.bytes,archiveFiles:restored.archiveFiles,
    directory:relative(process.cwd(),directory).split(sep).join('/'),
    scope:'Fresh isolated restore and source integrity; no new acquisition, derivation or publication'};
  await writeFile(join(directory,'accepted-publication.json'),JSON.stringify(report,null,2)+'\n');
  await writeFile('reviews/personnel-runtime-restore.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
}
main().catch(error=>{
  let detail=error instanceof Error?error.message:'Unknown failure';
  for(const [key,value]of Object.entries(process.env))if(value&&/token|secret|password|key/i.test(key))detail=detail.split(value).join('[redacted]');
  console.error('Personnel restore failed:',detail.slice(0,1000));process.exitCode=1;
});
