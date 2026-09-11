import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {mkdir,open,unlink,writeFile} from 'node:fs/promises';
import {personnelPipeline} from './personnel_pipeline';
const execute=promisify(execFile);

async function main(){
  const args=process.argv.slice(2);
  if(args.length>1||args.some(a=>a!=='--publish'))throw Error('Use no arguments for a real collection rehearsal, or --publish');
  await mkdir('release-recovery',{recursive:true});
  const path='release-recovery/personnel-worker.lock';
  const lock=await open(path,'wx');
  const startedAt=new Date().toISOString(),stages:{script:string;startedAt:string;finishedAt?:string;status:string}[]=[];
  let result:Awaited<ReturnType<typeof personnelPipeline>>|undefined;
  try{
    await lock.writeFile(JSON.stringify({pid:process.pid,startedAt}));
    for(const name of ['personnel-pipeline','personnel-runtime-restore','personnel-runtime-refresh',
      'personnel-refresh-replay','personnel-incremental-package','personnel-incremental-publication','personnel-public-readback']){
      await unlink(`reviews/${name}.json`).catch(error=>{if(error.code!=='ENOENT')throw error;});
    }
    result=await personnelPipeline(async(runtime,argv)=>{
      console.log('Personnel step:',argv[0]);
      const stage={script:argv[0],startedAt:new Date().toISOString(),status:'failed',finishedAt:''};stages.push(stage);
      try{
        const {stdout}=await execute(runtime==='node'?process.execPath:'python',runtime==='node'?['--import','tsx',...argv]:argv,
          {cwd:process.cwd(),env:process.env,timeout:argv[0]==='scripts/refresh_personnel_worker.py'?1200000:600000,maxBuffer:2_000_000,windowsHide:true});
        const parsed=JSON.parse(stdout.trim().split(/\r?\n/).at(-1)!);
        stage.status='completed';return parsed;
      }finally{stage.finishedAt=new Date().toISOString();}
    },args.includes('--publish'));
    console.log(JSON.stringify({publication:result.publication,derivationFailure:result.refreshed.derivationFailure}));
  }finally{
    try{await writeFile('reviews/personnel-pipeline.json',JSON.stringify({startedAt,finishedAt:new Date().toISOString(),
      status:result?'completed':'failed',stages,...result,
      scope:'Current pipeline attempt; public reader and scheduled execution require separate checks'},null,2)+'\n');}
    finally{await lock.close();await unlink(path);}
  }
}
main().catch(error=>{
  let detail=error instanceof Error?error.message:'Unknown failure';
  for(const [key,value]of Object.entries(process.env))if(value&&/token|secret|password|key/i.test(key))detail=detail.split(value).join('[redacted]');
  console.error('Personnel pipeline failed:',detail.slice(0,1000));process.exitCode=1;
});
