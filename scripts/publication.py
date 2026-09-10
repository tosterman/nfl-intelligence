"""Publication receipts are separate from generated forecasts and game results."""
from datetime import datetime
import hashlib,json

def snapshot_valid(snapshot):
    payload={k:v for k,v in snapshot.items() if k!='hash'}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()==snapshot.get('hash')

def verify_append_only(previous,current):
    if current[:len(previous)]!=previous:raise ValueError('Existing forecast snapshots cannot be altered or removed')
    hashes=[s['hash'] for s in current]
    if len(hashes)!=len(set(hashes)):raise ValueError('Duplicate snapshot hash')

def eligible_snapshot(game,ledger,receipts):
    if not game.get('kickoff'):return None
    cutoff=datetime.fromisoformat(game['kickoff'])
    eligible=[]
    for s in ledger:
        if s['gameId']!=game['id']:continue
        if not snapshot_valid(s):continue
        created=datetime.fromisoformat(s.get('generatedAt',s.get('publishedAt')))
        if created>=cutoff:continue
        for r in receipts:
            if r.get('status')!='ready' or s['hash'] not in r.get('snapshotHashes',[]):continue
            published=datetime.fromisoformat(r['publishedAt'])
            if created<=published<cutoff and r.get('deploymentUrl','').startswith('https://'):
                eligible.append((created,published,s));break
    return max(eligible,key=lambda x:(x[0],x[1]))[2] if eligible else None

def grade_prospective(games,ledger,receipts):
    records=[];missed=0;ties=0
    for g in games:
        if g['status']!='final':continue
        s=eligible_snapshot(g,ledger,receipts)
        if s is None:missed+=1;continue
        actual=g['actualHome']-g['actualAway'];p=s['prediction']['homeWinProbability']
        if actual==0:ties+=1;continue
        outcome=int(actual>0)
        records.append({'gameId':g['id'],'snapshotHash':s['hash'],'probability':p,'outcome':outcome,'correct':int((p>=.5)==bool(outcome)),'brier':(p-outcome)**2})
    n=len(records)
    return {'games':n,'wins':sum(r['correct'] for r in records),'ties':ties,'missed':missed,'brier':sum(r['brier'] for r in records)/n if n else None,'records':records}
