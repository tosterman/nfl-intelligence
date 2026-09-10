"""Offline development experiment. Never writes production artifacts.

Select on 2021-22, scale residuals on 2023, report 2024-25 as development.
Historical EPA uses current revised upstream models: not vintage reconstruction.
"""
import csv, hashlib, json, math, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import build_data as base

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'
URL='https://github.com/nflverse/nflverse-data/releases/download/stats_team/stats_team_week_{}.csv'
NAMES=['pass EPA/dropback','rush EPA/carry','CPOE','sack rate','interception rate','fumble loss/play','pass share']

def download(season):
    p=RAW/f'stats_team_week_{season}.csv'
    if not p.exists():p.write_bytes(urllib.request.urlopen(URL.format(season),timeout=60).read())
    with p.open(encoding='utf-8-sig') as f:records=list(csv.DictReader(f))
    return records,{'url':URL.format(season),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'retrievedAt':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'season':season,'rows':len(records),'latestWeek':max((int(r['week']) for r in records),default=None),'license':'CC BY 4.0','licenseUrl':'https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md','timestampMeaning':'Local acquisition time; upstream publication and vintage availability unverified.'}

def rates(r):
    f=lambda k:float(r.get(k) or 0)
    db=max(1,f('attempts')+f('sacks_suffered'));ru=max(1,f('carries'));plays=db+ru
    return np.array([f('passing_epa')/db,f('rushing_epa')/ru,f('passing_cpoe'),f('sacks_suffered')/db,f('passing_interceptions')/db,f('fumbles_lost_total')/plays,db/plays])

def summarize(pred,actual,sigma=None):
    err=pred-actual
    if sigma is None:sigma=np.sqrt(np.mean(err**2,axis=0))
    mask=actual[:,0]!=0
    p=np.array([.5*(1+math.erf(v/(sigma[0]*2**.5))) for v in pred[mask,0]])
    y=(actual[mask,0]>0).astype(float)
    return {'games':len(pred),'margin_mae':float(abs(err[:,0]).mean()),'total_mae':float(abs(err[:,1]).mean()),'brier':float(((p-y)**2).mean()),'accuracy':float(((p>=.5)==y).mean()),'margin_rmse':float(np.sqrt((err[:,0]**2).mean())),'coverage80':float((abs(err[:,0])<=1.28155*sigma[0]).mean())}

def features(rows,statmap,half=180):
    hist={t:[] for t in base.TEAMS};out=[];active=[]
    weeks={}
    for r in rows:weeks.setdefault((r['season'],r['week'],r['game_type']),[]).append(r)
    for games in sorted(weeks.values(),key=lambda rs:rs[0]['gameday']):
        day=datetime.fromisoformat(min(r['gameday'] for r in games)).toordinal()
        def avg(t):
            h=[x for x in hist[t] if x[0]<day and x[0]>day-1460]
            if not h:return np.zeros(14)
            w=np.array([2**(-(day-x[0])/half) for x in h]);v=np.array([x[1] for x in h])
            return np.sum(w[:,None]*v,axis=0)/(w.sum()+2)
        for r in games:
            if r['season']>=2014:
                h=avg(r['home_team']);a=avg(r['away_team'])
                # Pair each offense's past rates with opposing defense's allowed rates.
                # Additive rate matchups, not causal interaction claims.
                fh=np.r_[h[:7],a[7:]];fa=np.r_[a[:7],h[7:]]
                out.append(np.r_[1,0 if r['location']=='Neutral' else 1,fh-fa,fh+fa])
                active.append(r)
        for r in games:
            h=statmap.get((r['game_id'],r['home_team']));a=statmap.get((r['game_id'],r['away_team']))
            if h is None or a is None:continue
            date=datetime.fromisoformat(r['gameday']).toordinal()
            hist[r['home_team']].append((date,np.r_[h,a]));hist[r['away_team']].append((date,np.r_[a,h]))
    return np.array(out),active

def fit_symmetric(x,y,ridge=100):
    """Fit disjoint structural designs, returning coefficients in raw units.

    Margin: venue plus differences, without centering or an intercept.
    Total: intercept, venue and sums. All scaling uses training data only.
    A neutral team swap negates margin and preserves total by construction.
    """
    beta=np.zeros((x.shape[1],2))
    for output,columns in [(0,np.arange(1,16)),(1,np.r_[0,1,np.arange(16,30)])]:
        design=x[:,columns]
        if output==0:
            mean=np.zeros(len(columns));scale=np.sqrt(np.mean(design**2,axis=0))
        else:
            mean=design.mean(axis=0);mean[0]=0
            scale=design.std(axis=0)
        scale[scale<1e-8]=1
        normalized=(design-mean)/scale
        penalty=np.eye(len(columns))*ridge
        if output==1:penalty[0,0]=0
        fitted=np.linalg.solve(normalized.T@normalized+penalty,normalized.T@y[:,output])
        beta[columns,output]=fitted/scale
        if output==1:beta[0,output]-=float(mean@(fitted/scale))
    return beta

def linear_replay(x,rows,ridge=100):
    years=np.array([r['season'] for r in rows]);dates=np.array([datetime.fromisoformat(r['gameday']).toordinal() for r in rows])
    y=np.array([[r['home_score']-r['away_score'],r['home_score']+r['away_score']] for r in rows])
    out=np.zeros_like(y);cache={}
    for i,r in enumerate(rows):
        if r['season']<2021:continue
        key=(r['season'],r['week'],r['game_type'])
        if key not in cache:
            day=min(dates[j] for j,g in enumerate(rows) if (g['season'],g['week'],g['game_type'])==key)
            tr=(dates<day)&(years>=2014)
            cache[key]=fit_symmetric(x[tr],y[tr],ridge)
        out[i]=x[i]@cache[key]
    return out,y,years

def infer_epa(history,statmap,targets,half=90,ridge=10):
    """Pregame EPA inference; target scores/stats never enter their own features.

    Caller must filter history to known completed games at its real availability
    cutoff. This offline method cannot certify historical source availability.
    Contributions sum to unrounded predicted margin; neutral intercept is zero.
    """
    target_ids={r['game_id'] for r in targets}
    earlier=[r for r in history if r['game_id'] not in target_ids and r['home_score'] is not None and r['away_score'] is not None]
    merged=sorted(earlier+targets,key=lambda r:(r['gameday'],r['game_id']))
    x,records=features(merged,statmap,half)
    out={}
    target_weeks={(r['season'],r['week'],r['game_type']) for r in targets}
    cutoff=min(r['gameday'] for r in merged if (r['season'],r['week'],r['game_type']) in target_weeks)
    tr=np.array([r['gameday']<cutoff and r['game_id'] not in target_ids and r['home_score'] is not None and r['away_score'] is not None for r in records])
    if int(tr.sum())<500:raise ValueError('Insufficient historical feature rows')
    y=np.array([[r['home_score']-r['away_score'],r['home_score']+r['away_score']] for r,ok in zip(records,tr) if ok])
    beta=fit_symmetric(x[tr],y,ridge)
    names=['League baseline','Home venue']+[f'{kind} {side} {name}' for kind in ['difference','sum'] for side in ['offense','opponent allowed'] for name in NAMES]
    for i,r in enumerate(records):
        if r['game_id'] not in target_ids:continue
        pred=x[i]@beta
        terms=x[i]*beta[:,0]
        out[r['game_id']]={'homeMargin':float(pred[0]),'total':float(pred[1]),'homeScore':float((pred[1]+pred[0])/2),'awayScore':float((pred[1]-pred[0])/2),'trainingGames':int(tr.sum()),'trainingThrough':max(g['gameday'] for g,ok in zip(records,tr) if ok),'contributions':[{'name':name,'points':float(v)} for name,v in zip(names,terms)],'featureValues':dict(zip(names,map(float,x[i])))}
    return out

def infer_blend(history,statmap,targets,weight=.25,score_params=(180,6),epa_params=(90,10)):
    """Validation-selected blend; returns evidence, leaves probability scale to caller."""
    ep=infer_epa(history,statmap,targets,*epa_params)
    target_weeks={(r['season'],r['week'],r['game_type']) for r in targets}
    cutoff=min(r['gameday'] for r in history+targets if (r['season'],r['week'],r['game_type']) in target_weeks)
    beta,n,last=base.fit(history,cutoff,*score_params)
    result={}
    for r in targets:
        sc=base.predict(beta,r);p=ep[r['game_id']]
        # Preserve full precision through blending and attribution; round only UI.
        venue=0 if r['location']=='Neutral' else .5
        h=float(base.vector(r['home_team'],r['away_team'],venue)@beta)
        a=float(base.vector(r['away_team'],r['home_team'],-venue)@beta)
        sc.update(homeScore=h,awayScore=a,homeMargin=h-a,total=h+a)
        sc['contributions'][0]['points']=float(beta[2+base.IDX[r['home_team']]]-beta[2+base.IDX[r['away_team']]])
        sc['contributions'][1]['points']=float(beta[34+base.IDX[r['away_team']]]-beta[34+base.IDX[r['home_team']]])
        sc['contributions'][2]['points']=float(2*venue*beta[1])
        margin=(1-weight)*sc['homeMargin']+weight*p['homeMargin'];total=(1-weight)*sc['total']+weight*p['total']
        terms=[{**c,'points':(1-weight)*c['points']} for c in sc['contributions']]+[{'name':'EPA model: '+c['name'],'points':weight*c['points']} for c in p['contributions']]
        result[r['game_id']]={'homeMargin':margin,'total':total,'homeScore':(total+margin)/2,'awayScore':(total-margin)/2,'contributions':terms,'epa':p,'score':sc,'trainingThrough':last,'trainingGames':n}
    return result

def main():
    RAW.mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as pool:downloads=list(pool.map(download,range(2010,2026)))
    statmap={(r['game_id'],base.team(r['team'])):rates(r) for records,_ in downloads for r in records}
    rows=[r for r in base.load_rows(ROOT/'data/games.csv') if r['home_score'] is not None and r['away_score'] is not None and r['season']<=2025]
    trials=[];predictions={}
    # Declared grid: scoring shrinkage first, selected by validation margin MAE only.
    for half in [90,180,270,365,540]:
        for ridge in [1,3,6,12,20,60]:
            p=base.replay(rows,[2021,2022],(half,ridge));m=base.metrics(p)
            trials.append({'family':'score','half':half,'ridge':ridge,'margin_mae':m['marginMae'],'total_mae':m['totalMae']})
    best=min(trials,key=lambda t:t['margin_mae'])
    score=base.replay(rows,[2021,2022,2023,2024,2025],(best['half'],best['ridge']))
    original=base.replay(rows,[2021,2022,2023,2024,2025],(180,20))
    for name,pp in [('score_selected',score),('original_180_20',original)]:
        predictions[name]={p['id']:np.array([p['homeMargin'],p['total']]) for p in pp}
    epa=[]
    for half in [90,180,365]:
        x,active=features(rows,statmap,half)
        for ridge in [10,100,1000]:
            pred,y,years=linear_replay(x,active,ridge)
            m=summarize(pred[np.isin(years,[2021,2022])],y[np.isin(years,[2021,2022])],np.array([14,14]))
            t={'family':'epa','half':half,'ridge':ridge,**m};epa.append(t)
            predictions[f'epa_{half}_{ridge}']={r['game_id']:v for r,v in zip(active,pred)}
    eb=min(epa,key=lambda t:t['margin_mae']);ename=f"epa_{eb['half']}_{eb['ridge']}"
    active=[r for r in rows if r['season']>=2021];years=np.array([r['season'] for r in active]);actual=np.array([[r['home_score']-r['away_score'],r['home_score']+r['away_score']] for r in active])
    sc=np.array([predictions['score_selected'][r['game_id']] for r in active]);ep=np.array([predictions[ename][r['game_id']] for r in active])
    blends=[]
    for weight in [0,.25,.5,.75,1]:
        v=weight*ep+(1-weight)*sc;m=summarize(v[np.isin(years,[2021,2022])],actual[np.isin(years,[2021,2022])],np.array([14,14]));blends.append({'epa_weight':weight,**m})
    weight=min(blends,key=lambda t:t['margin_mae'])['epa_weight']
    evaluations={}
    for name,v in [('score_selected',sc),('epa_selected',ep),('blend_selected',weight*ep+(1-weight)*sc),('original_180_20',np.array([predictions['original_180_20'][r['game_id']] for r in active]))]:
        sigma=np.sqrt(np.mean((v[years==2023]-actual[years==2023])**2,axis=0))
        evaluations[name]={'sigma_2023':sigma.tolist(),'validation':summarize(v[np.isin(years,[2021,2022])],actual[np.isin(years,[2021,2022])],np.array([14,14])),'development':summarize(v[np.isin(years,[2024,2025])],actual[np.isin(years,[2024,2025])],sigma),'seasons':{str(s):summarize(v[years==s],actual[years==s],sigma) for s in [2024,2025]}}
    result={'score_grid':trials,'epa_grid':epa,'blend_grid':blends,'selected_score':best,'selected_epa':eb,'selected_blend_weight':weight,'evaluations':evaluations,'sources':[s for _,s in downloads],'stats_rows':len(statmap)}
    result['structure']='symmetric-v2: margin venue+differences without intercept; total intercept+venue+sums'
    (ROOT/'reviews/symmetry-experiment-results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:result[k] for k in ['selected_score','selected_epa','selected_blend_weight','evaluations']},indent=2),flush=True)

if __name__=='__main__':main()
