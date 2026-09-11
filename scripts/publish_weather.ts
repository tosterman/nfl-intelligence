import {mkdir,writeFile} from 'node:fs/promises';
import {prepareWeatherPublication} from './weather_publication_inputs';
import {weatherBlobStore} from '../src/lib/weather-blob';
import {decodeWeatherBundle,assertWeatherContinuity} from '../src/lib/weather-bundle';
import {readWeatherObjects,publishWeatherObjects} from '../src/lib/weather-publication';

async function main(){
  const args=process.argv.slice(2);
  if(args.some(arg=>arg!=='--publish')||args.length>1)throw Error('Use no arguments for rehearsal, or --publish');
  const {bundle,objects}=prepareWeatherPublication(process.cwd());
  const previous=await readWeatherObjects(weatherBlobStore,[0]);
  if(previous){
    const prior=decodeWeatherBundle(previous.objects[0]);
    if(prior.weather.generatedAt!==previous.generatedAt)throw Error('Stored weather timestamp differs');
    assertWeatherContinuity(prior,bundle);
  }
  const publish=args.includes('--publish');
  const manifestHash=publish?await publishWeatherObjects(objects,bundle.weather.generatedAt,weatherBlobStore,previous?.manifestHash??null):null;
  if(publish){
    const actual=await readWeatherObjects(weatherBlobStore,[0]);
    if(actual?.manifestHash!==manifestHash||!actual.objects[0].equals(objects[0]))throw Error('Published weather readback differs');
  }
  const report={checkedAt:new Date().toISOString(),mode:publish?'published':'read-only-rehearsal',objects:objects.length,
    generatedAt:bundle.weather.generatedAt,previousManifestHash:previous?.manifestHash??null,manifestHash,
    retainedObservations:bundle.history.records.length,scope:'Storage publication does not establish public page availability'};
  await mkdir('release-recovery',{recursive:true});
  await writeFile('release-recovery/weather-publication-report.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
}
main().catch(error=>{
  let detail=error instanceof Error?error.message:'Unknown failure';
  for(const [key,value] of Object.entries(process.env))if(value&&/token|secret|password|key/i.test(key))detail=detail.split(value).join('[redacted]');
  console.error('Weather publication failed:',detail.slice(0,1000));process.exitCode=1;
});
