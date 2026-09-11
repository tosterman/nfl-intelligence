import 'server-only';
import {cache} from 'react';
import {unstable_cache} from 'next/cache';
import {weatherBlobStore} from './weather-blob';
import {readWeatherPartitionPointer} from './weather-partition-publication';
import {readWeatherPartitionSnapshot,readWeatherGamePartition,readWeatherPartitionIndex,readWeatherGamePartitionObject} from './weather-partition-store';
import {boundWeatherRecord} from './weather-bundle';
import type {WeatherHistory} from './weather-history';
import type {WeatherRecord} from './weather';
import {site} from './data';
import locations from '../../data/weather-venues.json';
import extraLocations from '../../data/weather-osm-venues.json';
import {weatherBrief, type ContextBrief} from './context-briefing';

const readPublished=unstable_cache(async()=>{
  try{
    const stored=await readWeatherPartitionPointer(weatherBlobStore);
    if(!stored)return null;
    const bundle=await readWeatherPartitionSnapshot(weatherBlobStore,stored.root);
    return {bundle,root:stored.root,manifestHash:stored.publication.sha256};
  }catch{console.error('Published weather unavailable');return null;}
},['weather-publication-v2'],{revalidate:60,tags:['published-weather']});

// Immutable references are part of each cache key. Freshness is checked after retrieval.
const readBriefingIndex=unstable_cache(async(root:Parameters<typeof readWeatherPartitionIndex>[1])=>
  readWeatherPartitionIndex(weatherBlobStore,root),['weather-briefing-index-v1'],{revalidate:false});
const readBriefingHistory=unstable_cache(async(root:Parameters<typeof readWeatherGamePartitionObject>[1],gameId:string,ref:Parameters<typeof readWeatherGamePartitionObject>[3])=>
  (await readWeatherGamePartitionObject(weatherBlobStore,root,gameId,ref)).history,
  ['weather-briefing-history-v1'],{revalidate:false});

// One selection per render; all views use the same snapshot/history pair.
export const getWeather=cache(async(gameId?:string, briefingAt?:number)=>{
  const stored=await readPublished();
  const venues={...locations,...extraLocations};
  const games:Record<string,WeatherRecord>={};
  if(stored)for(const game of site.games){
    const record=boundWeatherRecord(stored.bundle,game,venues);
    if(record)games[game.id]=record;
  }
  let history:WeatherHistory={schemaVersion:1,records:[]};
  const briefs:ContextBrief[]=[];
  if(stored && briefingAt !== undefined){
    let index:Awaited<ReturnType<typeof readBriefingIndex>>={};
    try{index=await readBriefingIndex(stored.root);}catch{console.error('Published briefing weather index unavailable');}
    const upcoming=site.games.filter(game=>game.status!=='final' && Date.parse(game.kickoff??'')>briefingAt &&
      Date.parse(game.kickoff??'')<=briefingAt+7*86400000 && games[game.id] && Object.hasOwn(index,game.id));
    // A single selected publication binds every partition; only summaries cross the client boundary.
    for(let i=0;i<upcoming.length;i+=4){
      const batch=await Promise.all(upcoming.slice(i,i+4).map(async game=>{
        try{
          const history=await readBriefingHistory(stored.root,game.id,index[game.id]);
          return weatherBrief(history,games[game.id],game,briefingAt);
        }catch{console.error('Published briefing weather history unavailable');return null;}
      }));
      briefs.push(...batch.filter((row):row is ContextBrief=>row!==null));
    }
  }
  if(stored&&gameId&&site.games.some(game=>game.id===gameId)){
    try{history=(await readWeatherGamePartition(weatherBlobStore,stored.root,gameId))?.history??history;}
    catch{console.error('Published game weather history unavailable');}
  }
  return {snapshot:{collectionStartedAt:stored?.bundle.weather.collectionStartedAt??'',
    generatedAt:stored?.bundle.weather.generatedAt??'',games},
    history,briefs,manifestHash:stored?.manifestHash??null};
});
