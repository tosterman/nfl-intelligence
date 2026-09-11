import type {WeatherObjectStore} from './weather-publication';

/** Invalidate in-flight v1 CAS writes; updated v1 writers reject the frozen pointer. */
export async function freezeLegacyWeather(store:WeatherObjectStore,expectedManifestHash:string){
 const path='weather/latest.json',previous=await store.read(path);
 if(!previous||!previous.etag||previous.body.length>4096)throw Error('Missing legacy publication for migration');
 const value=JSON.parse(previous.body.toString());
 if(value?.schemaVersion!==1||value.manifestHash!==expectedManifestHash||!/^[a-f0-9]{64}$/.test(expectedManifestHash))throw Error('Legacy publication changed before freeze');
 if(value.frozenForMigration===true)return;
 const frozen=Buffer.from(JSON.stringify({...value,frozenForMigration:true}));
 try{await store.write(path,frozen,previous.etag);}catch(error){
  const actual=await store.read(path);
  if(!actual?.body.equals(frozen))throw error;
 }
 const actual=await store.read(path);
 if(!actual?.body.equals(frozen))throw Error('Legacy freeze readback differs');
}
