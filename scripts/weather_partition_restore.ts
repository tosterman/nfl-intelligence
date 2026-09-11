import {existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {execFileSync} from 'node:child_process';
import type {WeatherObjectStore} from '../src/lib/weather-publication';
import {readWeatherPartitionPointer} from '../src/lib/weather-partition-publication';
import {readWeatherPartitionIndex,readWeatherGamePartitionObject} from '../src/lib/weather-partition-store';

export async function restoreWeatherPartitions(root:string,store:Pick<WeatherObjectStore,'read'>,gameIds:string[]){
 if(existsSync(join(root,'data/weather-ledger.json')))throw Error('Partition restore requires a fresh worker ledger');
 if(new Set(gameIds).size!==gameIds.length||gameIds.length>1000)throw Error('Invalid weather restore scope');
 const previous=await readWeatherPartitionPointer(store);
 if(!previous)throw Error('Partitioned weather publication is required');
 const index=await readWeatherPartitionIndex(store,previous.root),ledgers:string[]=[];
 const sources=new Map<string,Buffer>();
 for(const id of gameIds){
  if(!Object.hasOwn(index,id))continue;
  const partition=await readWeatherGamePartitionObject(store,previous.root,id,index[id]);
  ledgers.push(partition.ledgerJson);
  for(const [identity,ref] of Object.entries(partition.sources)){
   if(sources.has(identity))continue;
   const stored=await store.read('weather/objects/'+ref.sha256);
   if(!stored||stored.body.length!==ref.bytes||createHash('sha256').update(stored.body).digest('hex')!==ref.sha256||
      createHash('sha256').update(gunzipSync(stored.body,{maxOutputLength:10_000_000})).digest('hex')!==identity)throw Error('Restored weather source differs');
   sources.set(identity,stored.body);
  }
 }
 mkdirSync(join(root,'data/weather-sources'),{recursive:true});
 for(const [identity,body] of sources){
  const path=join(root,'data/weather-sources',identity+'.json.gz');
  if(existsSync(path)){if(!readFileSync(path).equals(body))throw Error('Existing worker source differs');}
  else writeFileSync(path,body,{flag:'wx'});
 }
 const code="import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from weather_history import verify_record;from publication import write_receipts;root=Path(sys.argv[2]);rows=[row for ledger in json.load(sys.stdin) for row in json.loads(ledger)];assert len({r['hash'] for r in rows})==len(rows),'Duplicate restored history';\nfor row in rows:verify_record(row,root)\nwrite_receipts(root/'data/weather-ledger.json',rows);print(len(rows))";
 const observations=Number(execFileSync('python',['-c',code,resolve('scripts'),resolve(root)],{input:JSON.stringify(ledgers),timeout:60000,maxBuffer:1_000_000}).toString().trim());
 return {publication:previous.publication.sha256,restoredGames:ledgers.length,observations,sources:sources.size};
}
