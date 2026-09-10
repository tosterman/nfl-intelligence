"""Freeze pregame research matrices; publication verification is separate."""
import gzip,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import urlopen
import numpy as np
import build_data as base
from evaluate_joint_scores import priors
from joint_scores import reconcile_scores
from publication import snapshot_valid
ROOT=Path(__file__).resolve().parents[1]

def verify_frozen(reference,prior_hashes,code_hashes,fit):
    if fit!=reference['fit'] or prior_hashes!=reference['priorHashes'] or any(code_hashes.get(k)!=v for k,v in reference['codeHashes'].items()):raise ValueError('Frozen research distribution changed; new protocol required')

def eligible_games(local,public,now):
    if local['modelVersion']!=public['modelVersion'] or local['generatedAt']!=public['generatedAt']:raise ValueError('Public edition differs')
    remote={g['id']:g for g in public['games']}
    if len(remote)!=len(public['games']):raise ValueError('Duplicate public game')
    selected=[]
    for g in local['games']:
        if not g.get('snapshot') or not g.get('kickoff') or g['status']=='final':continue
        if datetime.fromisoformat(g['kickoff'])<=now:continue
        if not snapshot_valid(g['snapshot']):raise ValueError('Invalid local snapshot hash')
        other=remote.get(g['id'])
        if not other or any(other.get(k)!=g.get(k) for k in ['home','away','kickoff','snapshot']):raise ValueError('Public forecast mismatch')
        if datetime.fromisoformat(g['snapshot'].get('generatedAt',g['snapshot'].get('publishedAt')))>=now:raise ValueError('Forecast generation is not prior')
        selected.append(g)
    return selected

def main():
    path=ROOT/'data/site.json';raw=path.read_bytes();site=json.loads(raw)
    if site['modelVersion']!='score-efficiency-v1.2.0':raise ValueError('Frozen shadow baseline changed')
    with urlopen('https://nfl-intelligence-one.vercel.app/api/forecasts',timeout=20) as response:public_raw=response.read()
    now=datetime.now(timezone.utc);games=eligible_games(site,json.loads(public_raw),now)
    if not games:raise ValueError('No eligible future games')
    source=ROOT/'data/games.csv';candidate,reference,fit=priors(base.load_rows(source));records=[]
    prior_hashes={k:hashlib.sha256(p.tobytes()).hexdigest() for k,p in [('candidate',candidate),('reference',reference)]}
    code_hashes={n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in ['capture_joint_shadow.py','evaluate_joint_scores.py','joint_scores.py','build_data.py','publication.py']}
    frozen_path=ROOT/'reviews/joint-shadow-reference.json'
    verify_frozen(json.loads(frozen_path.read_text()),prior_hashes,code_hashes,fit)
    for g in games:
        prediction=g['snapshot']['prediction'];tie=fit['tieProbability'] if g['type']=='REG' else 0
        records.append({'gameId':g['id'],'season':g['season'],'week':g['week'],'type':g['type'],'home':g['home'],'away':g['away'],'kickoff':g['kickoff'],'pointSnapshot':g['snapshot'],
            'candidate':reconcile_scores(candidate,prediction['homeScore'],prediction['awayScore'],tie).tolist(),
            'reference':reconcile_scores(reference,prediction['homeScore'],prediction['awayScore'],tie).tolist()})
    if any(datetime.fromisoformat(r['kickoff'])<=datetime.now(timezone.utc) for r in records):raise ValueError('Kickoff passed during capture')
    report={'schemaVersion':1,'generatedAt':now.isoformat(),'status':'research-unpublished','scoreGrid':'rows=home,columns=away;integer0..100','modelVersion':site['modelVersion'],
        'siteArtifactHash':hashlib.sha256(raw).hexdigest(),'publicForecastResponseHash':hashlib.sha256(public_raw).hexdigest(),'scheduleHash':hashlib.sha256(source.read_bytes()).hexdigest(),'fit':fit,'numpyVersion':np.__version__,
        'priorHashes':prior_hashes,'frozenReferenceHash':hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
        'protocolHash':hashlib.sha256((ROOT/'reviews/joint-shadow-protocol.md').read_bytes()).hexdigest(),
        'codeHashes':code_hashes,'records':records}
    payload=json.dumps(report,sort_keys=True,separators=(',',':'),allow_nan=False).encode();digest=hashlib.sha256(payload).hexdigest();compressed=gzip.compress(payload,mtime=0)
    folder=ROOT/'reviews/joint-shadow';folder.mkdir(exist_ok=True)
    filename=digest+'.json.gz';destination=folder/filename
    with destination.open('xb') as output:output.write(compressed)
    manifest={'generatedAt':report['generatedAt'],'archive':'reviews/joint-shadow/'+filename,'sha256':digest,'compressedHash':hashlib.sha256(compressed).hexdigest(),'compressedBytes':len(compressed),'games':len(records),'earliestKickoff':min(r['kickoff'] for r in records),'status':'awaiting-publication-verification'}
    (folder/(digest+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
