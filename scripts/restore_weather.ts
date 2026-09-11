import {weatherBlobStore} from '../src/lib/weather-blob';
import {readWeatherObjects} from '../src/lib/weather-publication';
import {restoreWeatherArchive} from './weather_restore';

async function main(){
  const stored=await readWeatherObjects(weatherBlobStore);
  if(!stored)throw Error('Published weather history is absent; bootstrap explicitly before scheduled collection');
  const result=restoreWeatherArchive(process.cwd(),stored.objects);
  console.log(JSON.stringify({manifestHash:stored.manifestHash,...result}));
}
main().catch(error=>{console.error('Weather restore failed:',error instanceof Error?error.name:'UnknownError');process.exitCode=1;});
