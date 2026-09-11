import {readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import type {PersonnelRef} from '../src/lib/personnel-publication';

/** Load a locally replayed bootstrap package, never arbitrary manifest paths. */
export async function loadPersonnelBootstrap(directory:string,initial=true){
  const raw=await readFile(join(directory,'candidate.json'));
  if(raw.length>1_000_000)throw Error('Personnel candidate manifest too large');
  const manifest=JSON.parse(raw.toString());
  if(!Array.isArray(manifest.objects)||manifest.objects.length<1||manifest.objects.length>5002||
    manifest.objectCount!==manifest.objects.length||new Set(manifest.objects).size!==manifest.objects.length||
    manifest.objects.some((id:unknown)=>typeof id!=='string'||!/^[a-f0-9]{64}$/.test(id)))
    throw Error('Invalid personnel candidate object inventory');
  const objects=new Map<string,Buffer>();let bytes=0;
  for(const id of manifest.objects as string[]){
    const body=await readFile(join(directory,id));bytes+=body.length;
    if(!body.length||body.length>10_000_000||bytes>64_000_000||createHash('sha256').update(body).digest('hex')!==id)
      throw Error('Personnel candidate bytes differ');
    objects.set(id,body);
  }
  const publication=manifest.publication as PersonnelRef;
  const body=objects.get(publication?.sha256);
  if(!body||body.length!==publication.bytes||bytes!==manifest.bytes)
    throw Error('Personnel candidate root or size differs');
  if(initial&&JSON.parse(body.toString()).previous!==null)throw Error('Bootstrap requires an initial publication');
  return {publication,objects};
}
