import 'server-only';
import {cache} from 'react';
import {unstable_cache} from 'next/cache';
import {weatherBlobStore} from './weather-blob';
import {readWeatherObjects} from './weather-publication';
import {decodeWeatherBundle,boundWeatherRecord} from './weather-bundle';
import type {WeatherRecord} from './weather';
import {site} from './data';
import locations from '../../data/weather-venues.json';
import extraLocations from '../../data/weather-osm-venues.json';

const readPublished=unstable_cache(async()=>{
  try{
    const stored=await readWeatherObjects(weatherBlobStore,[0]);
    if(!stored)return null;
    const bundle=decodeWeatherBundle(stored.objects[0]);
    if(bundle.weather.generatedAt!==stored.generatedAt)throw Error('Weather publication timestamp differs');
    return {bundle,manifestHash:stored.manifestHash};
  }catch{console.error('Published weather unavailable');return null;}
},['weather-publication-v1'],{revalidate:60,tags:['published-weather']});

// One selection per render; all views use the same snapshot/history pair.
export const getWeather=cache(async()=>{
  const stored=await readPublished();
  const venues={...locations,...extraLocations};
  const games:Record<string,WeatherRecord>={};
  if(stored)for(const game of site.games){
    const record=boundWeatherRecord(stored.bundle,game,venues);
    if(record)games[game.id]=record;
  }
  return {snapshot:{collectionStartedAt:stored?.bundle.weather.collectionStartedAt??'',
    generatedAt:stored?.bundle.weather.generatedAt??'',games},
    history:stored?.bundle.history??{schemaVersion:1,records:[]},manifestHash:stored?.manifestHash??null};
});
