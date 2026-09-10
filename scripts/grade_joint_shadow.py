"""Grade verified archived research matrices; never regenerate distributions."""
import hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from evaluate_joint_scores import score
from verify_joint_shadow import verify_capture
from capture_joint_shadow import verify_frozen
from publication import snapshot_valid
from benchmark_uncertainty import compare
ROOT=Path(__file__).resolve().parents[1]

def load_shadows(folder):
    reference=json.loads((ROOT/'reviews/joint-shadow-reference.json').read_text())
    scorer_hash=hashlib.sha256((ROOT/'scripts/evaluate_joint_scores.py').read_bytes()).hexdigest()
    if scorer_hash!=reference['codeHashes']['evaluate_joint_scores.py']:raise ValueError('Frozen scoring implementation changed; version grading explicitly')
    protocol_hash=hashlib.sha256((ROOT/'reviews/joint-shadow-protocol.md').read_bytes()).hexdigest()
    shadows=[]
    for path in sorted(folder.glob('*.publication.json')):
        receipt=json.loads(path.read_text());digest=receipt['sha256']
        if not re.fullmatch('[a-f0-9]{64}',digest) or path.name!=digest+'.publication.json' or not re.fullmatch('[a-f0-9]{40}',receipt['commit']):raise ValueError('Invalid receipt identity')
        archive='reviews/joint-shadow/'+digest+'.json.gz'
        if receipt['status']!='verified-before-kickoff' or receipt['archive']!=archive or receipt['url']!='https://raw.githubusercontent.com/tosterman/nfl-intelligence/'+receipt['commit']+'/'+archive:raise ValueError('Invalid publication source')
        manifest=json.loads((folder/(digest+'.manifest.json')).read_text())
        if receipt['compressedHash']!=manifest['compressedHash'] or digest!=manifest['sha256']:raise ValueError('Receipt hash mismatch')
        data=verify_capture(manifest,(folder/(digest+'.json.gz')).read_bytes(),datetime.fromisoformat(receipt['observedAt']),datetime.fromisoformat(receipt['githubHttpDate']))
        if receipt['generatedAt']!=data['generatedAt'] or receipt['gameIds']!=[r['gameId'] for r in data['records']] or data['protocolHash']!=protocol_hash:raise ValueError('Receipt scope or protocol mismatch')
        verify_frozen(reference,data['priorHashes'],data['codeHashes'],data['fit'])
        for r in data['records']:
            if not snapshot_valid(r['pointSnapshot']):raise ValueError('Point snapshot hash mismatch')
            shadows.append({'archiveHash':digest,'publishedAt':receipt['observedAt'],'generatedAt':data['generatedAt'],'record':r})
    return shadows

def grade(shadows,games,now):
    by_id={g['id']:g for g in games}
    if len(by_id)!=len(games):raise ValueError('Duplicate result identity')
    selected={}
    for s in sorted(shadows,key=lambda s:(datetime.fromisoformat(s['publishedAt']),s['archiveHash'])):
        r=s['record'];published=datetime.fromisoformat(s['publishedAt']);kickoff=datetime.fromisoformat(r['kickoff'])
        if not datetime.fromisoformat(s['generatedAt'])<=published<kickoff or published>now:raise ValueError('Invalid prospective publication time')
        selected.setdefault(r['gameId'],s)
    results=[]
    for game_id,s in selected.items():
        r=s['record'];g=by_id.get(game_id)
        row={'gameId':game_id,'archiveHash':s['archiveHash'],'publishedAt':s['publishedAt'],'season':r['season'],'week':r['week']}
        if not g:
            results.append(row|{'status':'pending','reason':'Game missing from current result source'});continue
        if any(g.get(k)!=r.get(k) for k in ['home','away','season','week','type']) or not g.get('kickoff') or datetime.fromisoformat(g['kickoff'])!=datetime.fromisoformat(r['kickoff']):
            results.append(row|{'status':'excluded','reason':'Matchup or kickoff changed; reconciliation required'});continue
        if g['status']!='final' or g.get('actualHome') is None or g.get('actualAway') is None:
            results.append(row|{'status':'pending','reason':'Verified final score unavailable'});continue
        if datetime.fromisoformat(g['kickoff'])>=now:raise ValueError('Final result predates kickoff')
        actual=[g['actualHome'],g['actualAway']]
        if any(type(x) not in (int,float) or not np.isfinite(x) or x<0 or x!=int(x) for x in actual):raise ValueError('Invalid final score')
        row|={'status':'graded','actualHome':actual[0],'actualAway':actual[1]}
        for name in ['candidate','reference']:
            mass=np.asarray(r[name],dtype=float)
            if mass.shape!=(101,101):raise ValueError('Archived grid differs from protocol')
            row[name]=score(mass,*actual)
        results.append(row)
    scored=[r for r in results if r['status']=='graded']
    keys=['jointLogScore','marginLogScore','totalLogScore','marginCrps','totalCrps','threeOutcomeBrier']
    paired=None
    if scored:
        comparison=compare([{'id':r['gameId'],'season':r['season'],'week':r['week'],'candidate':r['candidate']['jointLogScore'],'reference':r['reference']['jointLogScore'],'zero':0} for r in scored],'candidate','reference','zero')
        paired={k:comparison[k] for k in ['difference','interval95','clustersBySeason','draws','seed']}
    return {'graded':len(scored),'pending':sum(r['status']=='pending' for r in results),'excluded':sum(r['status']=='excluded' for r in results),
        'pairedJointLogScore':paired,
        'summary':{name:{k:float(np.mean([r[name][k] for r in scored])) for k in keys} for name in ['candidate','reference']} if scored else None,'records':results}

def main():
    path=ROOT/'data/site.json';raw=path.read_bytes();site=json.loads(raw);now=datetime.now(timezone.utc)
    report=grade(load_shadows(ROOT/'reviews/joint-shadow'),site['games'],now)
    report.update(checkedAt=now.isoformat(),resultArtifactHash=hashlib.sha256(raw).hexdigest(),meaning='Separate prospective research track. First verified capture per game; archived probabilities only. Missing results are pending, changed identities excluded, zero graded games are not zero error.',
        codeHashes={n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in ['grade_joint_shadow.py','verify_joint_shadow.py','capture_joint_shadow.py','evaluate_joint_scores.py','benchmark_uncertainty.py']})
    (ROOT/'reviews/joint-shadow-performance.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
if __name__=='__main__':main()
