import {copyFileSync,cpSync,mkdirSync,mkdtempSync,readFileSync,readdirSync,writeFileSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {execFileSync} from 'node:child_process';
import {weatherBlobStore} from '../src/lib/weather-blob';
import {restoreWeatherPartitions} from './weather_partition_restore';
import {prepareWeatherPartitionCandidate} from './weather_partition_inputs';
import {publishWeatherPartitions} from '../src/lib/weather-partition-publication';
let stage='configuration';

async function main(){
 const args=process.argv.slice(2);
 if(args.length>1||args.some(arg=>arg!=='--publish'))throw Error('Use no arguments for collection rehearsal or --publish');
 mkdirSync('release-recovery',{recursive:true});
 const root=mkdtempSync(resolve('release-recovery/weather-worker-v2-'));
 mkdirSync(join(root,'data'));mkdirSync(join(root,'scripts'));
 for(const name of readdirSync('scripts'))if(name.endsWith('.py'))copyFileSync(join('scripts',name),join(root,'scripts',name));
 for(const name of ['site.json','weather-venues.json','weather-osm-venues.json'])copyFileSync(join('data',name),join(root,'data',name));
 cpSync('data/weather-location-sources',join(root,'data/weather-location-sources'),{recursive:true});
 const site=JSON.parse(readFileSync(join(root,'data/site.json'),'utf8')),now=Date.now();
 const ids=site.games.filter((g:{kickoff:string|null})=>{const at=Date.parse(g.kickoff??'');return at>now&&at-now<=7*86400000;}).map((g:{id:string})=>g.id);
 stage='restore';
 const restored=await restoreWeatherPartitions(root,weatherBlobStore,ids);
 stage='collection';
 execFileSync('python',['scripts/refresh_weather.py'],{cwd:root,timeout:600000,maxBuffer:2_000_000});
 execFileSync('python',['scripts/weather_history.py'],{cwd:root,timeout:60000,maxBuffer:1_000_000});
 stage='verify';
 const prepared=await prepareWeatherPartitionCandidate(root,weatherBlobStore);
 if(prepared.previous!==restored.publication)throw Error('Weather publication changed during collection; restore and collect again');
 stage='publication';
 const result=args.includes('--publish')?await publishWeatherPartitions(prepared.candidate,weatherBlobStore,prepared.previous):null;
 const publicationRoot=JSON.parse(prepared.candidate.objects.get(prepared.candidate.publication.sha256)!.toString());
 const report={checkedAt:new Date().toISOString(),mode:result?'published':'collection-rehearsal',restored,
  generatedAt:publicationRoot.generatedAt,manifestHash:prepared.candidate.publication.sha256,...prepared.summary,result,
  scope:'Scoped collection and storage publication; public website readback is separate'};
 writeFileSync('release-recovery/weather-publication-report.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report));
}
main().catch(error=>{
 const failure=error instanceof Error?error.name:'UnknownError';
 mkdirSync('release-recovery',{recursive:true});
 writeFileSync('release-recovery/weather-publication-report.json',JSON.stringify({checkedAt:new Date().toISOString(),mode:'failed',stage,failure})+'\n');
 console.error('Partitioned weather collection failed:',stage,failure);process.exitCode=1;
});
