"""Production publication artifact builder; all persisted forecasts are append-only."""
import csv,hashlib,json,math,os,subprocess,tempfile,urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import build_data as base
import experiment_model as efficiency
from publication import verify_append_only,grade_prospective

ROOT=base.ROOT
SOURCE='https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv'
VERSION='score-efficiency-v1.2.0'
CONFIG={'scoreHalfLifeDays':180,'scoreRidge':6,'efficiencyHalfLifeDays':90,'efficiencyRidge':10,'efficiencyWeight':.25,'selectionSeasons':[2021,2022],'residualSeason':2023,'evaluationSeasons':[2024,2025],'protocol':'weekly-freeze'}

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def validate_schedule(rows):
    seen=set()
    for r in rows:
        if not r['game_id'] or r['game_id'] in seen:raise ValueError('Duplicate or empty game identifier')
        seen.add(r['game_id'])
        if r['home_team'] not in base.IDX or r['away_team'] not in base.IDX or r['home_team']==r['away_team']:raise ValueError('Invalid matchup')
        datetime.fromisoformat(r['gameday'])
        if r['gametime']:base.kickoff(r)
        scores=[r['home_score'],r['away_score']]
        if (scores[0] is None)!=(scores[1] is None):raise ValueError('Incomplete final score')
        if any(v is not None and (not math.isfinite(v) or v<0 or v!=int(v)) for v in scores):raise ValueError('Invalid final score')
    if not rows:raise ValueError('Empty schedule')

def acquire():
    raw=ROOT/'data/games.csv';meta_path=ROOT/'data/source.json'
    if os.environ.get('NFL_OFFLINE')!='1':
        payload=urllib.request.urlopen(SOURCE,timeout=45).read()
        if not payload.startswith(b'game_id,') or len(payload)<100000:raise ValueError('Invalid schedule input')
        # Parse and validate a staging file before replacing the last usable cache.
        staged=None
        try:
            with tempfile.NamedTemporaryFile(dir=raw.parent,suffix='.csv',delete=False) as stream:
                stream.write(payload);staged=Path(stream.name)
            rows=base.load_rows(staged);validate_schedule(rows)
            staged.replace(raw)
        finally:
            if staged is not None:staged.unlink(missing_ok=True)
        meta={'url':SOURCE,'sha256':hashlib.sha256(payload).hexdigest(),'retrievedAt':datetime.now(timezone.utc).isoformat(),'license':'CC BY 4.0','licenseUrl':'https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md'}
        meta_path.write_text(json.dumps(meta,indent=2)+'\n')
    else:
        meta=json.loads(meta_path.read_text())
        if meta['sha256']!=hashlib.sha256(raw.read_bytes()).hexdigest():raise ValueError('Offline source digest mismatch')
    rows=base.load_rows(raw);validate_schedule(rows)
    return rows,meta

def canonical_prediction(margin,total,sigmas,contributions,profiles=None):
    if not all(math.isfinite(v) for v in [margin,total,*sigmas]) or min(sigmas)<=0 or not 0<(total-abs(margin))/2<=70 or (total+abs(margin))/2>70:raise ValueError('Invalid projection')
    p=.5*(1+math.erf(margin/(sigmas[0]*math.sqrt(2))))
    if not 0<round(p,5)<1:raise ValueError('Unsupported degenerate win probability')
    out={'homeScore':round((total+margin)/2,2),'awayScore':round((total-margin)/2,2),'homeMargin':round(margin,3),'total':round(total,3),'homeWinProbability':round(p,5),'marginInterval80':[round(margin-1.28155*sigmas[0],1),round(margin+1.28155*sigmas[0],1)],'totalInterval80':[round(total-1.28155*sigmas[1],1),round(total+1.28155*sigmas[1],1)],'sigmaMargin':round(sigmas[0],3),'sigmaTotal':round(sigmas[1],3),'contributions':contributions,'profiles':profiles or []}
    return out

def evidence(blend):
    grouped={c['name']:c['points'] for c in blend['contributions'][:3]}
    grouped['Efficiency baseline']=0
    for c in blend['contributions'][3:]:
        name=c['name']
        if 'pass EPA' in name:key='Passing efficiency'
        elif 'rush EPA' in name:key='Rushing efficiency'
        elif 'CPOE' in name:key='Completion quality'
        elif 'sack rate' in name:key='Pass protection & pressure'
        elif 'interception' in name or 'fumble' in name:key='Turnover profile'
        elif 'pass share' in name:key='Pass frequency'
        elif 'Home venue' in name:key='Home field'
        else:key='Efficiency baseline'
        grouped[key]=grouped.get(key,0)+c['points']
    terms=[{'name':k,'points':round(v,3),'detail':'Weighted statistical contribution from prior games; not a causal player effect.'} for k,v in grouped.items()]
    remainder=round(blend['homeMargin']-sum(c['points'] for c in terms),3)
    if remainder:terms.append({'name':'Rounding reconciliation','points':remainder,'detail':'Reconciles displayed rounded contributions.'})
    return terms

def replay_blend(rows,statmap):
    completed=[r for r in rows if r['home_score'] is not None and r['away_score'] is not None and r['season']<=2025]
    score=base.replay(completed,[2023,2024,2025],(180,6));sc={p['id']:p for p in score}
    x,active=efficiency.features(completed,statmap,90);pred,actual,years=efficiency.linear_replay(x,active,10)
    blended={r['game_id']:(.75*np.array([sc[r['game_id']]['homeMargin'],sc[r['game_id']]['total']])+.25*pred[i]) for i,r in enumerate(active) if r['game_id'] in sc}
    residual=np.array([blended[r['game_id']]-actual[i] for i,r in enumerate(active) if r['season']==2023]);sigmas=np.sqrt(np.mean(residual**2,axis=0))
    records=[]
    for r in active:
        if r['season'] not in [2024,2025]:continue
        margin,total=blended[r['game_id']];p=canonical_prediction(float(margin),float(total),sigmas,[])
        p.update({k:sc[r['game_id']][k] for k in ['id','season','week','actualMargin','actualTotal','marketMargin','marketTotal','trainingThrough']});p['gameType']=r['game_type'];records.append(p)
    return records,sigmas

def profiles_for(r,statmap,rows,cutoff):
    result=[]
    for code in [r['away_team'],r['home_team']]:
        prior=[g for g in rows if g['gameday']<cutoff and code in [g['home_team'],g['away_team']] and g['home_score'] is not None and (g['game_id'],code) in statmap and (datetime.fromisoformat(cutoff)-datetime.fromisoformat(g['gameday'])).days<1460]
        w=np.array([2**(-(datetime.fromisoformat(cutoff)-datetime.fromisoformat(g['gameday'])).days/90) for g in prior])
        values=np.array([statmap[(g['game_id'],code)] for g in prior]);allowed=np.array([statmap[(g['game_id'],g['away_team'] if g['home_team']==code else g['home_team'])] for g in prior])
        if not len(prior):continue
        avg=(w[:,None]*values).sum(axis=0)/w.sum();defense=(w[:,None]*allowed).sum(axis=0)/w.sum()
        result.append({'team':code,'games':len(prior),'through':prior[-1]['gameday'],'passEpa':round(float(avg[0]),3),'rushEpa':round(float(avg[1]),3),'cpoe':round(float(avg[2]),2),'sackRate':round(float(avg[3]),4),'passEpaAllowed':round(float(defense[0]),3),'rushEpaAllowed':round(float(defense[1]),3)})
    return result

def main():
    now=datetime.now(timezone.utc);rows,source=acquire();season=max(r['season'] for r in rows if r['gameday']<=now.date().isoformat());current=[r for r in rows if r['season']==season]
    # Missing current kickoff times are not replaced with an invented late-night time.
    scheduled=[r for r in current if r['gametime'] and base.kickoff(r)>now]
    week=scheduled[0]['week'] if scheduled else current[-1]['week'];week_rows=[r for r in current if r['week']==week]
    cutoff=min(r['gameday'] for r in week_rows)
    efficiency.RAW.mkdir(parents=True,exist_ok=True)
    def get_stats(year):
        path=efficiency.RAW/f'stats_team_week_{year}.csv'
        if year>=season-1 and os.environ.get('NFL_OFFLINE')!='1':
            payload=urllib.request.urlopen(efficiency.URL.format(year),timeout=45).read()
            if b'passing_epa' not in payload[:8000]:raise ValueError('Malformed efficiency source')
            path.write_bytes(payload)
        return efficiency.download(year)
    with ThreadPoolExecutor(max_workers=5) as pool:downloads=list(pool.map(get_stats,range(2010,season+1)))
    statmap={(r['game_id'],base.team(r['team'])):efficiency.rates(r) for records,_ in downloads for r in records}
    # Missing source fields must fail closed rather than becoming zero-valued features.
    for records,_ in downloads:
        for row in records:
            for field in ['passing_epa','rushing_epa','passing_cpoe','attempts','carries','sacks_suffered','passing_interceptions','fumbles_lost_total']:
                if row.get(field) in ('',None):raise ValueError(f'Missing efficiency field {field} in {row.get("game_id")}')
    known=[r for r in rows if r['gameday']<cutoff and r['season']>=2010 and r['home_score'] is not None]
    required={(r['game_id'],t) for r in known for t in [r['home_team'],r['away_team']]}
    if required-set(statmap):raise ValueError('Efficiency data coverage incomplete; retain previous publication')
    records,sigmas=replay_blend(rows,statmap)
    targets=[r for r in week_rows if r['gametime'] and base.kickoff(r)>now]
    predictions=efficiency.infer_blend(rows,statmap,targets) if targets else {}
    beta,n,last=base.fit(rows,cutoff,180,6)
    ledger_path=ROOT/'data/ledger.json';previous=json.loads(ledger_path.read_text()) if ledger_path.exists() else [];ledger=list(previous)
    model_digest=hashlib.sha256(b''.join((ROOT/'scripts'/p).read_text().replace('\r\n','\n').encode() for p in ['build_data.py','experiment_model.py','refresh.py'])).hexdigest()
    now=datetime.now(timezone.utc)
    for r in targets:
        if base.kickoff(r)<=now:continue
        blend=predictions[r['game_id']];p=canonical_prediction(blend['homeMargin'],blend['total'],sigmas,evidence(blend),profiles_for(r,statmap,rows,cutoff))
        existing=[s for s in ledger if s['gameId']==r['game_id']]
        if existing and existing[-1]['modelVersion']==VERSION and existing[-1]['prediction']==p and existing[-1].get('modelCodeHash')==model_digest:continue
        snap={'gameId':r['game_id'],'modelVersion':VERSION,'generatedAt':now.isoformat(),'trainingGames':n,'trainingThrough':last,'prediction':p,'sourceHash':source['sha256'],'sourceRetrievedAt':source['retrievedAt'],'efficiencyRetrievedAt':max(m['retrievedAt'] for _,m in downloads),'efficiencySourceHashes':[m['sha256'] for _,m in downloads],'modelCodeHash':model_digest,'configuration':CONFIG}
        snap['hash']=digest(snap);ledger.append(snap)
    verify_append_only(previous,ledger)
    games=[]
    for r in current:
        kick=base.kickoff(r).isoformat() if r['gametime'] else None
        history=[s for s in ledger if s['gameId']==r['game_id'] and kick and datetime.fromisoformat(s.get('generatedAt',s.get('publishedAt')))<datetime.fromisoformat(kick)]
        status='final' if r['home_score'] is not None and r['away_score'] is not None else 'scheduled' if not kick or datetime.fromisoformat(kick)>now else 'in-progress'
        games.append({'id':r['game_id'],'season':season,'week':r['week'],'type':r['game_type'],'home':r['home_team'],'away':r['away_team'],'kickoff':kick,'venue':r['stadium'],'neutral':r['location']=='Neutral','roof':r['roof'],'status':status,'actualHome':r['home_score'],'actualAway':r['away_score'],'snapshot':history[-1] if history else None,'history':history,'market':None,'weather':None,'injuries':None})
    ratings=[{'team':t,'offense':round(float(beta[2+base.IDX[t]]),2),'defense':round(float(-beta[34+base.IDX[t]]),2),'rating':round(float(beta[2+base.IDX[t]]-beta[34+base.IDX[t]]),2)} for t in base.TEAMS];ratings.sort(key=lambda t:-t['rating'])
    receipts=json.loads((ROOT/'data/publications.json').read_text())
    output={'generatedAt':now.isoformat(),'season':season,'week':week,'modelVersion':VERSION,'source':source,'efficiencySources':[m for _,m in downloads],'model':{'parameters':{'halfLifeDays':180,'ridge':6},'configuration':CONFIG,'trainingGames':n,'trainingThrough':last,'weeklyCutoff':cutoff,'sigmaMargin':float(sigmas[0]),'sigmaTotal':float(sigmas[1]),'homeField':round(float(beta[1]),3),'baselineScore':round(float(beta[0]),3)},'games':games,'ratings':ratings,'livePerformance':grade_prospective(games,ledger,receipts),'performance':{'label':'Retrospective development evaluation','seasons':[2024,2025],'aggregate':base.metrics(records),'bySeason':[{'season':s,**base.metrics([p for p in records if p['season']==s])} for s in [2024,2025]],'byPhase':[{'phase':label,**base.metrics([p for p in records if (p['gameType']=='REG')==regular])} for label,regular in [('Regular season',True),('Postseason',False)]],'records':records}}
    # Write only after every model and ledger validation succeeds.
    ledger_path.write_text(json.dumps(ledger,indent=2)+'\n');(ROOT/'data/site.json').write_text(json.dumps(output,separators=(',',':'))+'\n')
    print(json.dumps({'model':VERSION,'games':len(games),'snapshots':len(ledger),'generatedAt':now.isoformat(),'metrics':output['performance']['aggregate']},indent=2))
if __name__=='__main__':main()
