import 'server-only';
import {cache} from 'react';
import {unstable_cache} from 'next/cache';
import {weatherBlobStore} from './weather-blob';
import {readWeatherPartitionPointer} from './weather-partition-publication';
import {readWeatherPartitionSnapshot,readWeatherGamePartition} from './weather-partition-store';
import {boundWeatherRecord} from './weather-bundle';
import type {WeatherHistory} from './weather-history';
import type {WeatherRecord} from './weather';
import {site} from './data';
import locations from '../../data/weather-venues.json';
import extraLocations from '../../data/weather-osm-venues.json';

const readPublished=unstable_cache(async()=>{
  try{
    const stored=await readWeatherPartitionPointer(weatherBlobStore);
    if(!stored)return null;
    const bundle=await readWeatherPartitionSnapshot(weatherBlobStore,stored.root);
    return {bundle,root:stored.root,manifestHash:stored.publication.sha256};
  }catch{console.error('Published weather unavailable');return null;}
},['weather-publication-v2'],{revalidate:60,tags:['published-weather']});

// One selection per render; all views use the same snapshot/history pair.
export const getWeather=cache(async(gameId?:string)=>{
  const stored=await readPublished();
  const venues={...locations,...extraLocations};
  const games:Record<string,WeatherRecord>={};
  if(stored)for(const game of site.games){
    const record=boundWeatherRecord(stored.bundle,game,venues);
    if(record)games[game.id]=record;
  }
  let history:WeatherHistory={schemaVersion:1,records:[]};
  if(stored&&gameId&&site.games.some(game=>game.id===gameId)){
    try{history=(await readWeatherGamePartition(weatherBlobStore,stored.root,gameId))?.history??history;}
    catch{console.error('Published game weather history unavailable');}
  }
  return {snapshot:{collectionStartedAt:stored?.bundle.weather.collectionStartedAt??'',
    generatedAt:stored?.bundle.weather.generatedAt??'',games},
    history,manifestHash:stored?.manifestHash??null};
});
