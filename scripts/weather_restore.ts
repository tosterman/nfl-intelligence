import {existsSync,mkdirSync,readFileSync,writeFileSync,renameSync,unlinkSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {createHash,randomUUID} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {execFileSync} from 'node:child_process';
import {isDeepStrictEqual} from 'node:util';
import {decodeWeatherBundle} from '../src/lib/weather-bundle';

export function restoreWeatherArchive(root:string,objects:Buffer[]){
  if(objects.length<2)throw Error('Incomplete weather archive');
  const bundle=decodeWeatherBundle(objects[0]);
  const hash=(b:Buffer)=>createHash('sha256').update(b).digest('hex');
  if(hash(objects[1])!==bundle.ledgerSha256||objects.length!==bundle.sourceHashes.length+2)throw Error('Weather archive identity differs');
  const incoming=JSON.parse(objects[1].toString());
  if(!Array.isArray(incoming))throw Error('Invalid weather ledger');
  const ledgerPath=join(root,'data/weather-ledger.json');
  const local=existsSync(ledgerPath)?JSON.parse(readFileSync(ledgerPath,'utf8')):[];
  const rows=new Map(local.map((row:{hash:string})=>[row.hash,row]));
  for(const row of incoming)if(rows.has(row.hash)&&!isDeepStrictEqual(rows.get(row.hash),row))throw Error('Local weather history conflict');
  const sources=bundle.sourceHashes.map((identity,index)=>{
    const body=objects[index+2];
    if(hash(gunzipSync(body,{maxOutputLength:10_000_000}))!==identity)throw Error('Weather source identity differs');
    const path=join(root,'data/weather-sources',identity+'.json.gz');
    if(existsSync(path)&&hash(gunzipSync(readFileSync(path),{maxOutputLength:10_000_000}))!==identity)throw Error('Local weather source conflict');
    return {path,body};
  });
  mkdirSync(join(root,'data/weather-sources'),{recursive:true});
  for(const {path,body} of sources)if(!existsSync(path)){
    const temporary=path+'.'+randomUUID()+'.tmp';
    try{writeFileSync(temporary,body,{flag:'wx'});renameSync(temporary,path);}finally{if(existsSync(temporary))unlinkSync(temporary);}
  }
  const temporary=join(root,'data','.restore-'+randomUUID()+'.json');
  try{
    writeFileSync(temporary,objects[1],{flag:'wx'});
    // Merge in Python to preserve float serialization used by observation hashes.
    const code="import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from weather_history import verify_record;from publication import write_receipts;root=Path(sys.argv[2]);path=root/'data/weather-ledger.json';local=json.loads(path.read_bytes()) if path.exists() else [];incoming=json.loads(Path(sys.argv[3]).read_bytes());rows={r['hash']:r for r in local};assert len(rows)==len(local),'Duplicate local history';\nfor r in incoming:\n verify_record(r,root)\n if r['hash'] in rows and rows[r['hash']]!=r: raise ValueError('Weather history conflict')\n rows[r['hash']]=r\nfor r in rows.values(): verify_record(r,root)\nwrite_receipts(path,list(rows.values()))";
    execFileSync('python',['-c',code,resolve('scripts'),resolve(root),resolve(temporary)],{timeout:60000,maxBuffer:1_000_000});
  }finally{if(existsSync(temporary))unlinkSync(temporary);}
  return {observations:incoming.length,sources:sources.length};
}
