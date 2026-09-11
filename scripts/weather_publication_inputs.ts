import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {decodeWeatherBundle} from '../src/lib/weather-bundle';

export function prepareWeatherPublication(root:string){
  const execute=(code:string)=>execFileSync('python',['-c',code],{cwd:root,maxBuffer:10_000_000,timeout:60000});
  const presentation=execute("import sys;sys.path.insert(0,'scripts');from weather_bundle import build,transport;sys.stdout.buffer.write(transport(build()))");
  const bundle=decodeWeatherBundle(presentation);
  const ledger=execute("import sys,json;from pathlib import Path;sys.path.insert(0,'scripts');from weather_bundle import encode;sys.stdout.buffer.write(encode(json.loads(Path('data/weather-ledger.json').read_bytes())))");
  const hash=(body:Buffer)=>createHash('sha256').update(body).digest('hex');
  if(hash(ledger)!==bundle.ledgerSha256)throw Error('Weather ledger changed during publication preparation');
  const sources=bundle.sourceHashes.map(identity=>{
    const body=readFileSync(join(root,'data/weather-sources',identity+'.json.gz'));
    if(body.length>2_000_000||hash(gunzipSync(body,{maxOutputLength:10_000_000}))!==identity)throw Error('Weather source changed during publication preparation');
    return body;
  });
  return {bundle,objects:[presentation,ledger,...sources]};
}
