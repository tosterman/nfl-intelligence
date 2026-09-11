import {writeFile} from 'node:fs/promises';
import {personnelBlobStore} from '../src/lib/personnel-blob';
import {publishPersonnelObjects} from '../src/lib/personnel-publication';
import {preparePersonnelIncremental} from './personnel_incremental_inputs';

async function main(){
  const [directory,mode,...extra]=process.argv.slice(2);
  if(!directory||(mode!==undefined&&mode!=='--publish')||extra.length)throw Error('Usage: package-directory [--publish]');
  const {input,previous}=await preparePersonnelIncremental(directory,personnelBlobStore);
  const result=mode==='--publish'?await publishPersonnelObjects(input,personnelBlobStore,previous):null;
  const report={checkedAt:new Date().toISOString(),mode:mode==='--publish'?'published':'predecessor-check',
    publication:input.publication,previous,result,scope:'Private personnel publication; live reader and scheduler require separate verification'};
  await writeFile('reviews/personnel-incremental-publication.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
}
main().catch(error=>{
  let detail=error instanceof Error?error.message:'Unknown failure';
  for(const [key,value]of Object.entries(process.env))if(value&&/token|secret|password|key/i.test(key))detail=detail.split(value).join('[redacted]');
  console.error('Personnel incremental publication failed:',detail.slice(0,1000));process.exitCode=1;
});
