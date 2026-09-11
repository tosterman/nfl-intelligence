import 'server-only';
import {cache} from 'react';
import {unstable_cache} from 'next/cache';
import {personnelBlobStore} from './personnel-blob';
import {readPersonnelPublication,readPersonnelArchiveObject} from './personnel-publication';
import {personnelEvidenceForGame} from './personnel-presentation';
import type {Game} from './types';

const readPublished=unstable_cache(async()=>{
  try{
    const stored=await readPersonnelPublication(personnelBlobStore);
    return stored?{presentation:stored.presentation,publication:stored.publication,root:stored.root}:null;
  }catch{console.error('Published personnel unavailable');return null;}
},['personnel-publication-v1'],{revalidate:60,tags:['published-personnel']});

export const getPersonnelPublication=cache(readPublished);
export const getParticipationSource=unstable_cache(async(root:Parameters<typeof readPersonnelArchiveObject>[1])=>{
  try{return JSON.parse((await readPersonnelArchiveObject(personnelBlobStore,root,'data/participation-source.json')).toString());}
  catch{return null;}
},['personnel-participation-source-v1'],{revalidate:60});

// Select one verified set per render. Source-age checks still run in the views.
export const getPersonnel=cache(async(game:Game)=>{
  const stored=await getPersonnelPublication();
  return stored?personnelEvidenceForGame(stored.presentation,game):null;
});
