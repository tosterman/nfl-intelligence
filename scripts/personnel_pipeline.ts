import {resolve,sep} from 'node:path';
import {isDeepStrictEqual} from 'node:util';
type Result=Record<string,any>;
type Run=(runtime:'node'|'python',args:string[])=>Promise<Result>;
function localDirectory(value:unknown){
  if(typeof value!=='string'||!resolve(value).startsWith(resolve('release-recovery')+sep))throw Error('Worker output directory outside recovery workspace');
  return value;
}

export async function personnelPipeline(run:Run,publish=false){
  const restored=await run('node',['scripts/restore_personnel_worker.ts']);
  const refreshed=await run('python',['scripts/refresh_personnel_worker.py',localDirectory(restored.directory),'--collect']);
  if(!isDeepStrictEqual(refreshed.previousPublication,restored.publication)||refreshed.previousCapture!==restored.capture)
    throw Error('Refresh did not use selected restoration');
  const candidate=localDirectory(refreshed.directory);
  await run('python',['scripts/replay_personnel_candidate.py',candidate,'--recurring']);
  const packaged=await run('python',['scripts/personnel_incremental_archive.py',candidate]);
  if(!isDeepStrictEqual(packaged.previousPublication,restored.publication)||packaged.previousCapture!==restored.capture)
    throw Error('Packaged predecessor differs');
  const publication=await run('node',['scripts/publish_personnel_incremental.ts',localDirectory(packaged.directory),...(publish?['--publish']:[])]);
  if(publication.publication?.sha256!==packaged.publication?.sha256||publication.previous!==restored.publication?.sha256)
    throw Error('Publication report differs from candidate');
  return {restored,refreshed,packaged,publication};
}
