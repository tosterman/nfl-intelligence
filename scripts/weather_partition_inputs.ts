import {execFileSync} from 'node:child_process';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import type {WeatherObjectStore} from '../src/lib/weather-publication';
import {readWeatherObjects} from '../src/lib/weather-publication';
import {decodeWeatherBundle} from '../src/lib/weather-bundle';
import {readWeatherPartitionPointer} from '../src/lib/weather-partition-publication';
import {readWeatherPartitionIndex,type WeatherObjectRef} from '../src/lib/weather-partition-store';

type Prepared={publication:WeatherObjectRef;objects:Map<string,Buffer>};
const encode=(value:Prepared)=>({publication:value.publication,objects:Object.fromEntries([...value.objects].map(([h,b])=>[h,b.toString('base64')]))});
function python(code:string,input?:unknown,root=process.cwd()){
 return execFileSync('python',['-c',code,resolve('scripts'),resolve(root)],{
  input:input===undefined?undefined:JSON.stringify(input),maxBuffer:64_000_000,timeout:60000,
 }).toString();
}
const imports="import sys,json,base64;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from weather_partitions import build_partitions,verify_migration,verify_partition_continuity;from weather_bundle import encode;";

export async function prepareWeatherPartitionCandidate(root:string,store:Pick<WeatherObjectStore,'read'>){
 const raw=JSON.parse(python(imports+"root=Path(sys.argv[2]);r=build_partitions(root);summary=verify_migration(root,r);print(json.dumps({'publication':r['publication'],'objects':{h:base64.b64encode(b).decode() for h,b in r['objects'].items()},'summary':summary}))",undefined,root));
 const candidate:Prepared={publication:raw.publication,objects:new Map(Object.entries(raw.objects).map(([h,b])=>[h,Buffer.from(b as string,'base64')]))};
 const previous=await readWeatherPartitionPointer(store);
 let legacyManifestHash:string|null=null;
 if(previous){
  const rootBody=await store.read('weather/objects/'+previous.publication.sha256);
  const indexBody=await store.read('weather/objects/'+previous.root.index.sha256);
  if(!rootBody||!indexBody)throw Error('Prior publication disappeared');
  const prior:Prepared={publication:previous.publication,objects:new Map([[previous.publication.sha256,rootBody.body],[previous.root.index.sha256,indexBody.body]])};
  const index=await readWeatherPartitionIndex(store,previous.root);
  const newRoot=JSON.parse(candidate.objects.get(candidate.publication.sha256)!.toString());
  const newIndex=JSON.parse(candidate.objects.get(newRoot.index.sha256)!.toString()).games;
  for(const [id,ref] of Object.entries(index))if(newIndex[id]?.sha256!==ref.sha256||newIndex[id]?.bytes!==ref.bytes){
   const saved=await store.read('weather/objects/'+ref.sha256);
   if(!saved)throw Error('Prior game partition disappeared');
   prior.objects.set(ref.sha256,saved.body);
  }
  python(imports+"v=json.load(sys.stdin);decode=lambda r:{'publication':r['publication'],'objects':{h:base64.b64decode(b,validate=True) for h,b in r['objects'].items()}};print(json.dumps(verify_partition_continuity(decode(v['previous']),decode(v['current']))))",{previous:encode(prior),current:encode(candidate)},root);
 }else{
  // First migration must preserve the actual published v1 ledger, not just local history.
  const legacy=await readWeatherObjects(store,[0,1]);
  if(!legacy)throw Error('Published v1 bootstrap history is required');
  const bundle=decodeWeatherBundle(legacy.objects[0]);
  const candidateRoot=JSON.parse(candidate.objects.get(candidate.publication.sha256)!.toString());
  if(Date.parse(candidateRoot.generatedAt)<Date.parse(legacy.generatedAt))throw Error('Candidate is older than published legacy weather');
  if(createHash('sha256').update(legacy.objects[1]).digest('hex')!==bundle.ledgerSha256)throw Error('Legacy ledger fingerprint differs');
  legacyManifestHash=legacy.manifestHash;
  python(imports+"v=json.load(sys.stdin);r=v['current'];objects={h:base64.b64decode(b,validate=True) for h,b in r['objects'].items()};pub=json.loads(objects[r['publication']['sha256']]);index=json.loads(objects[pub['index']['sha256']]);rows={};\nfor ref in index['games'].values():\n p=json.loads(objects[ref['sha256']]);rows.update({r['hash']:r for r in json.loads(p['ledgerJson'])})\nfor row in json.loads(base64.b64decode(v['legacy'],validate=True)):\n if row['hash'] not in rows or encode(row)!=encode(rows[row['hash']]):raise ValueError('Published legacy observation missing or changed')\nprint('Legacy observations preserved')",{current:encode(candidate),legacy:legacy.objects[1].toString('base64')},root);
 }
 return {candidate,previous:previous?.publication.sha256??null,legacyManifestHash,summary:raw.summary};
}
