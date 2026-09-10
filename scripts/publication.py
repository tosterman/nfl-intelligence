"""Publication receipts are separate from generated forecasts and game results."""
from datetime import datetime
import hashlib,json,math,os,tempfile
from pathlib import Path
from calibration import calibration_bins

def write_receipts(path,receipts):
    """Replace only after the complete ledger is written and flushed beside it."""
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,prefix='.publications-',suffix='.tmp',delete=False) as file:
            temporary=Path(file.name)
            json.dump(receipts,file,indent=2,allow_nan=False);file.write('\n')
            file.flush();os.fsync(file.fileno())
        os.replace(temporary,path)
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)

def snapshot_valid(snapshot):
    payload={k:v for k,v in snapshot.items() if k!='hash'}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()==snapshot.get('hash')

def verify_append_only(previous,current):
    if current[:len(previous)]!=previous:raise ValueError('Existing forecast snapshots cannot be altered or removed')
    hashes=[s['hash'] for s in current]
    if len(hashes)!=len(set(hashes)):raise ValueError('Duplicate snapshot hash')

CONTEXT_FIELDS=('season','week','type','home','away','kickoff','venue','neutral')

def context_matches(snapshot,game):
    context=snapshot.get('gameContext')
    if not isinstance(context,dict) or any(k not in context or k not in game or context[k] is None or game[k] is None for k in CONTEXT_FIELDS):return False
    if any(context[k]!=game[k] for k in CONTEXT_FIELDS if k!='kickoff'):return False
    try:
        original=datetime.fromisoformat(context['kickoff']);current=datetime.fromisoformat(game['kickoff'])
        return original.tzinfo is not None and current.tzinfo is not None and original==current
    except (ValueError,TypeError):return False

def eligible_snapshot(game,ledger,receipts):
    if not game.get('kickoff'):return None
    cutoff=datetime.fromisoformat(game['kickoff'])
    eligible=[]
    for s in ledger:
        if s['gameId']!=game['id']:continue
        if not context_matches(s,game):continue
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
    records=[];score_records=[];missed=0;ties=0
    for g in games:
        if g['status']!='final':continue
        s=eligible_snapshot(g,ledger,receipts)
        if s is None:missed+=1;continue
        actual=g['actualHome']-g['actualAway'];p=s['prediction']['homeWinProbability']
        prediction=s['prediction'];total=g['actualHome']+g['actualAway']
        score={'gameId':g['id'],'snapshotHash':s['hash'],'generatedAt':s.get('generatedAt',s.get('publishedAt')),
            'homeMargin':prediction['homeMargin'],'total':prediction['total'],'actualMargin':actual,'actualTotal':total,
            'marginError':abs(prediction['homeMargin']-actual),'totalError':abs(prediction['total']-total)}
        for field,value in [('margin',actual),('total',total)]:
            interval=prediction.get(field+'Interval80')
            score[field+'Covered80']=bool(interval[0]<=value<=interval[1]) if interval is not None else None
        score_records.append(score)
        if actual==0:ties+=1;continue
        outcome=int(actual>0)
        bounded=min(1-1e-8,max(1e-8,p))
        records.append({'gameId':g['id'],'snapshotHash':s['hash'],'probability':p,'outcome':outcome,'correct':int((p>=.5)==bool(outcome)),'brier':(p-outcome)**2,'logLoss':-math.log(bounded if outcome else 1-bounded)})
    n=len(records)
    result={'games':n,'wins':sum(r['correct'] for r in records),'ties':ties,'missed':missed,'brier':sum(r['brier'] for r in records)/n if n else None,'logLoss':sum(r['logLoss'] for r in records)/n if n else None,'records':records,'scoreGames':len(score_records),'scoreRecords':score_records}
    for field in ['margin','total']:
        covered=[r[field+'Covered80'] for r in score_records if r[field+'Covered80'] is not None]
        result[field+'Mae']=sum(r[field+'Error'] for r in score_records)/len(score_records) if score_records else None
        result[field+'IntervalGames']=len(covered)
        result[field+'IntervalCoverage']=sum(covered)/len(covered) if covered else None
    result['calibration']=calibration_bins(records)
    return result
