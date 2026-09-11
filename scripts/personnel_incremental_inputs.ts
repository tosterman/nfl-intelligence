import {isDeepStrictEqual} from 'node:util';
import {gunzipSync} from 'node:zlib';
import {loadPersonnelBootstrap} from './personnel_bootstrap_inputs';
import {readPersonnelPublication,readPersonnelArchiveObject,type PersonnelObjectStore,type PersonnelRoot} from '../src/lib/personnel-publication';

export async function preparePersonnelIncremental(directory:string,store:Pick<PersonnelObjectStore,'read'>){
  const input=await loadPersonnelBootstrap(directory,false);
  const root=JSON.parse(input.objects.get(input.publication.sha256)!.toString()) as PersonnelRoot;
  const current=await readPersonnelPublication(store);
  if(!current)throw Error('Incremental personnel publication requires a predecessor');
  if(current.publication.sha256===input.publication.sha256)return {input,previous:current.root.previous?.sha256??null};
  if(!isDeepStrictEqual(root.previous,current.publication))throw Error('Accepted personnel predecessor changed');
  const proofRef=root.archive['reviews/personnel-replay-proof.json'];
  const proof=JSON.parse(input.objects.get(proofRef?.sha256)?.toString()??'null');
  if(proof?.mode!=='recurring'||!isDeepStrictEqual(proof.previousPublication,current.publication)||
    typeof proof.previousCapture!=='string'||!/^[a-f0-9]{64}$/.test(proof.previousCapture)||
    proof.transitionReplayed!==true||proof.inputsUnchanged!==true)throw Error('Refresh proof does not bind accepted predecessor');
  const capturePath=`data/personnel-sources/${proof.previousCapture}.snapshot.json.gz`;
  if(!current.root.archive[capturePath]||!isDeepStrictEqual(root.archive[capturePath],current.root.archive[capturePath]))throw Error('Predecessor capture was not retained');
  const prior=JSON.parse(gunzipSync(await readPersonnelArchiveObject(store,current.root,capturePath),{maxOutputLength:10_000_000}).toString());
  if(!isDeepStrictEqual(prior,current.presentation.evidence.snapshot))throw Error('Transition predecessor differs from accepted reports');
  const next=JSON.parse(input.objects.get(root.presentation.sha256)?.toString()??'null');
  if(proof.derivationFailure&&(proof.derivedUsageWithheld!==true||!Array.isArray(proof.steps)||proof.steps.length||
    next?.derivation?.status!=='unavailable'||next?.evidence?.historical!==null||next?.evidence?.current!==null))
    throw Error('Degraded personnel publication must withhold derived usage');
  const nextSnapshot=JSON.parse(input.objects.get(root.archive['data/personnel.json']?.sha256)?.toString()??'null');
  if(!nextSnapshot||!isDeepStrictEqual(nextSnapshot,next?.evidence?.snapshot))throw Error('Candidate report snapshot differs from presentation');
  if(isDeepStrictEqual(nextSnapshot,prior)){
    if(!isDeepStrictEqual(root.archive['data/personnel-changes.json'],current.root.archive['data/personnel-changes.json'])||
      !current.root.archive['data/personnel-changes.json']||!isDeepStrictEqual(next.evidence.history,current.presentation.evidence.history))
      throw Error('Unchanged personnel capture must preserve accepted history');
  }
  for(const name of ['data/site.json','data/games.csv','reviews/player-registry-source.json',
    'reviews/player-identity-source.csv.gz','reviews/player-usage-source.csv.gz']){
    if(!current.root.archive[name]||!isDeepStrictEqual(root.archive[name],current.root.archive[name]))
      throw Error('Pinned personnel input changed during refresh');
  }
  return {input,previous:current.publication.sha256};
}
