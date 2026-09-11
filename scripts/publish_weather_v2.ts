import {mkdir,writeFile} from 'node:fs/promises';
import {prepareWeatherPartitionCandidate} from './weather_partition_inputs';
import {weatherBlobStore} from '../src/lib/weather-blob';
import {readWeatherObjects} from '../src/lib/weather-publication';
import {publishWeatherPartitions} from '../src/lib/weather-partition-publication';
import {freezeLegacyWeather} from '../src/lib/weather-migration-freeze';

async function main(){
 const args=process.argv.slice(2);
 if(args.length>1||args.some(arg=>arg!=='--publish'))throw Error('Use no arguments for rehearsal or --publish');
 const prepared=await prepareWeatherPartitionCandidate(process.cwd(),weatherBlobStore);
 if(prepared.legacyManifestHash){
  const latest=await readWeatherObjects(weatherBlobStore,[0]);
  if(latest?.manifestHash!==prepared.legacyManifestHash)throw Error('Legacy publication changed during migration verification');
  if(args.includes('--publish'))await freezeLegacyWeather(weatherBlobStore,prepared.legacyManifestHash);
 }
 const result=args.includes('--publish')?await publishWeatherPartitions(prepared.candidate,weatherBlobStore,prepared.previous):null;
 const report={checkedAt:new Date().toISOString(),mode:result?'published':'read-only-rehearsal',
  publication:prepared.candidate.publication,previousPublication:prepared.previous,legacyManifestHash:prepared.legacyManifestHash,
  ...prepared.summary,result,scope:'Storage publication does not establish public page availability'};
 await mkdir('release-recovery',{recursive:true});
 await writeFile('release-recovery/weather-v2-publication-report.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report));
}
main().catch(error=>{
 let message=error instanceof Error?error.message:'Unknown failure';
 for(const [key,value] of Object.entries(process.env))if(value&&/token|secret|password|key/i.test(key))message=message.split(value).join('[redacted]');
 console.error('Partitioned weather publication failed:',message.slice(0,1000));process.exitCode=1;
});
