"""Reproducible, market-independent NFL scoring model and publishing pipeline.

Final historical scores are assumed available the following calendar day.
This is a results-only retrospective replay, not vintage data reconstruction.
"""
from __future__ import annotations
import csv, hashlib, json, math, os, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv'
VERSION = 'ridge-score-v1.0.0'
ALIASES = {'OAK':'LV','SD':'LAC','STL':'LA'}
TEAMS = sorted('ARI ATL BAL BUF CAR CHI CIN CLE DAL DEN DET GB HOU IND JAX KC LA LAC LV MIA MIN NE NO NYG NYJ PHI PIT SEA SF TB TEN WAS'.split())
IDX = {t:i for i,t in enumerate(TEAMS)}
PARAMS = [(180,20),(365,20),(365,60),(540,60)]

def team(t): return ALIASES.get(t,t)
def number(v): return float(v) if v not in ('',None) else None
def kickoff(row):
    return datetime.fromisoformat(row['gameday']+'T'+(row['gametime'] or '23:59')).replace(tzinfo=ZoneInfo('America/New_York')).astimezone(timezone.utc)
def vector(offense,defense,home):
    x=np.zeros(66); x[0]=1; x[1]=home; x[2+IDX[offense]]=1; x[34+IDX[defense]]=1
    return x
def load_rows(path):
    with path.open(encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    for r in rows:
        r['home_team']=team(r['home_team']);r['away_team']=team(r['away_team'])
        r['season']=int(r['season']);r['week']=int(r['week'])
        r['home_score']=number(r['home_score']);r['away_score']=number(r['away_score'])
    return sorted(rows,key=lambda r:(r['gameday'],r['game_id']))

def fit(rows,cutoff,half_life=365,ridge=60):
    history=[r for r in rows if r['gameday']<cutoff and r['home_score'] is not None and r['away_score'] is not None and r['gameday']>=str(int(cutoff[:4])-4)+'-01-01']
    if len(history)<100: raise ValueError('Insufficient historical games')
    x=[];y=[];weights=[]
    day=datetime.fromisoformat(cutoff)
    for r in history:
        neutral=r['location']=='Neutral'
        x.extend([vector(r['home_team'],r['away_team'],0 if neutral else .5), vector(r['away_team'],r['home_team'],0 if neutral else -.5)])
        y.extend([r['home_score'],r['away_score']])
        w=2**(-(day-datetime.fromisoformat(r['gameday'])).days/half_life)
        weights.extend([w,w])
    x=np.array(x); y=np.array(y); weights=np.array(weights)
    penalty=np.eye(66)*ridge;penalty[0,0]=0;penalty[1,1]=5
    beta=np.linalg.solve(x.T@(weights[:,None]*x)+penalty,x.T@(weights*y))
    return beta,len(history),history[-1]['gameday']

def predict(beta,r,sigma_margin=14,sigma_total=14):
    neutral=r['location']=='Neutral'
    h=float(vector(r['home_team'],r['away_team'],0 if neutral else .5)@beta)
    a=float(vector(r['away_team'],r['home_team'],0 if neutral else -.5)@beta)
    # Bounds are an explicit model guard, never silently clamp impossible scores.
    if min(h,a)<0 or max(h,a)>70: raise ValueError('Implausible expected score')
    margin=h-a;total=h+a
    p=.5*(1+math.erf(margin/(sigma_margin*math.sqrt(2))))
    home_off=float(beta[2+IDX[r['home_team']]]);away_off=float(beta[2+IDX[r['away_team']]])
    home_def=float(beta[34+IDX[r['home_team']]]);away_def=float(beta[34+IDX[r['away_team']]])
    return {'homeScore':round(h,2),'awayScore':round(a,2),'homeMargin':round(margin,3),'total':round(total,3),'homeWinProbability':round(p,5),
       'marginInterval80':[round(margin-1.28155*sigma_margin,1),round(margin+1.28155*sigma_margin,1)],
       'totalInterval80':[round(total-1.28155*sigma_total,1),round(total+1.28155*sigma_total,1)],
       'sigmaMargin':round(sigma_margin,3),'sigmaTotal':round(sigma_total,3),
       'contributions':[{'name':'Scoring offense','points':round(home_off-away_off,3),'detail':'Opponent-adjusted, recency-weighted scoring production.'},
                        {'name':'Scoring defense','points':round(away_def-home_def,3),'detail':'Opponent-adjusted points allowed; lower is better.'},
                        {'name':'Home field','points':round(0 if neutral else float(beta[1]),3),'detail':'Estimated from prior games; zero at neutral venues.'}]}

def replay(rows,seasons,params,sigmas=(14,14)):
    result=[];cache={}
    for r in rows:
        if r['season'] not in seasons or r['home_score'] is None or r['away_score'] is None: continue
        # Freeze ratings at each week's earliest game. Same-week outcomes never leak.
        key=(r['season'],r['week'],r['game_type'])
        if key not in cache:
            cutoff=min(g['gameday'] for g in rows if (g['season'],g['week'],g['game_type'])==key)
            cache[key]=fit(rows,cutoff,*params)
        beta,n,last=cache[key];p=predict(beta,r,*sigmas)
        p.update({'id':r['game_id'],'season':r['season'],'week':r['week'],'actualMargin':r['home_score']-r['away_score'],'actualTotal':r['home_score']+r['away_score'],'marketMargin':number(r['spread_line']),'marketTotal':number(r['total_line']),'trainingThrough':last})
        result.append(p)
    return result

def metrics(preds):
    decisive=[p for p in preds if p['actualMargin']!=0]
    if not decisive:return None
    prob=np.array([p['homeWinProbability'] for p in decisive]);y=np.array([float(p['actualMargin']>0) for p in decisive])
    margin_errors=np.array([p['homeMargin']-p['actualMargin'] for p in preds]);total_errors=np.array([p['total']-p['actualTotal'] for p in preds])
    calibration=[]
    for lo,hi in [(0,.4),(.4,.5),(.5,.6),(.6,.7),(.7,1.01)]:
        mask=(prob>=lo)&(prob<hi)
        if mask.any():calibration.append({'predicted':round(float(prob[mask].mean()),4),'observed':round(float(y[mask].mean()),4),'count':int(mask.sum()),'lower':lo,'upper':min(hi,1)})
    market=[p for p in preds if p['marketMargin'] is not None]
    ats={'wins':0,'losses':0,'pushes':0,'noPick':0}; totals=dict(ats)
    for p in preds:
        for tally,model,line,actual in [(ats,p['homeMargin'],p['marketMargin'],p['actualMargin']),(totals,p['total'],p['marketTotal'],p['actualTotal'])]:
            if line is None or abs(model-line)<2:tally['noPick']+=1
            elif actual==line:tally['pushes']+=1
            elif (model>line)==(actual>line):tally['wins']+=1
            else:tally['losses']+=1
    return {'games':len(preds),'decisiveGames':len(decisive),'ties':len(preds)-len(decisive),'wins':int(((prob>=.5)==y).sum()),'accuracy':round(float(((prob>=.5)==y).mean()),4),
       'brier':round(float(((prob-y)**2).mean()),4),'logLoss':round(float(-(y*np.log(np.clip(prob,1e-8,1-1e-8))+(1-y)*np.log(np.clip(1-prob,1e-8,1-1e-8))).mean()),4),
       'marginMae':round(float(abs(margin_errors).mean()),3),'totalMae':round(float(abs(total_errors).mean()),3),
       'homeBaselineAccuracy':round(float(y.mean()),4),'coinBrier':.25,'marketMarginMae':round(float(np.mean([abs(p['marketMargin']-p['actualMargin']) for p in market])),3) if market else None,
       'marketGames':len(market),'ats':ats,'totals':totals,'calibration':calibration,
       'intervalCoverage':round(float(np.mean([p['marginInterval80'][0]<=p['actualMargin']<=p['marginInterval80'][1] for p in preds])),4)}

def snapshot(r,p,now,n,last):
    obj={'gameId':r['game_id'],'modelVersion':VERSION,'publishedAt':now.isoformat(),'trainingGames':n,'trainingThrough':last,'prediction':p}
    obj['hash']=hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return obj

def main():
    now=datetime.now(timezone.utc);raw=ROOT/'data/games.csv'
    if os.environ.get('NFL_OFFLINE')!='1':
        with urllib.request.urlopen(SOURCE,timeout=30) as response:payload=response.read()
        # Parse downloaded bytes before replacing the last known input.
        if not payload.startswith(b'game_id,') or len(payload)<100000:raise ValueError('Invalid source response')
        raw.write_bytes(payload)
    rows=load_rows(raw)
    # Fixed chronology: parameters selected on 2021-22, residuals on 2023;
    # 2024-25 remain untouched until final evaluation.
    candidates=[]
    for param in PARAMS:
        validation=replay(rows,[2021,2022],param)
        score=metrics(validation)['marginMae'];candidates.append({'halfLifeDays':param[0],'ridge':param[1],'marginMae':score})
    best=min(candidates,key=lambda p:p['marginMae']);params=(best['halfLifeDays'],best['ridge'])
    residuals=replay(rows,[2023],params)
    sigmas=(float(np.sqrt(np.mean([(p['homeMargin']-p['actualMargin'])**2 for p in residuals]))),float(np.sqrt(np.mean([(p['total']-p['actualTotal'])**2 for p in residuals]))))
    heldout=replay(rows,[2024,2025],params,sigmas)
    season=max(r['season'] for r in rows if r['gameday']<=now.date().isoformat())
    current=[r for r in rows if r['season']==season]
    upcoming=[r for r in current if kickoff(r)>now]
    week=upcoming[0]['week'] if upcoming else current[-1]['week']
    beta,n,last=fit(rows,now.date().isoformat(),*params)
    ledger_path=ROOT/'data/ledger.json';ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    for r in current:
        if r['week']!=week or kickoff(r)<=now:continue
        existing=[s for s in ledger if s['gameId']==r['game_id']]
        p=predict(beta,r,*sigmas)
        if not existing or existing[-1]['prediction']!=p:ledger.append(snapshot(r,p,now,n,last))
    games=[]
    for r in current:
        snaps=[s for s in ledger if s['gameId']==r['game_id']]
        pre=[s for s in snaps if datetime.fromisoformat(s['publishedAt'])<kickoff(r)]
        chosen=pre[-1] if pre else None
        games.append({'id':r['game_id'],'season':season,'week':r['week'],'type':r['game_type'],'home':r['home_team'],'away':r['away_team'],
          'kickoff':kickoff(r).isoformat(),'venue':r['stadium'],'neutral':r['location']=='Neutral','roof':r['roof'],
          'status':'final' if r['home_score'] is not None else 'scheduled' if kickoff(r)>now else 'in-progress',
          'actualHome':r['home_score'],'actualAway':r['away_score'],'snapshot':chosen,'history':pre,'market':None,'weather':None,'injuries':None})
    ratings=[{'team':t,'offense':round(float(beta[2+IDX[t]]),2),'defense':round(float(-beta[34+IDX[t]]),2),'rating':round(float(beta[2+IDX[t]]-beta[34+IDX[t]]),2)} for t in TEAMS]
    ratings.sort(key=lambda t:-t['rating'])
    obj={'generatedAt':now.isoformat(),'season':season,'week':week,'modelVersion':VERSION,'source':{'url':SOURCE,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'retrievedAt':now.isoformat()},
      'model':{'parameters':best,'candidates':candidates,'trainingGames':n,'trainingThrough':last,'sigmaMargin':sigmas[0],'sigmaTotal':sigmas[1],'homeField':round(float(beta[1]),3),'baselineScore':round(float(beta[0]),3)},
      'games':games,'ratings':ratings,'performance':{'label':'Retrospective holdout','seasons':[2024,2025],'aggregate':metrics(heldout),'bySeason':[{'season':s,**metrics([p for p in heldout if p['season']==s])} for s in [2024,2025]],'records':heldout}}
    (ROOT/'data/site.json').write_text(json.dumps(obj,separators=(',',':'))+'\n')
    ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')
    print(json.dumps({'season':season,'week':week,'games':len(games),'snapshots':len(ledger),'parameters':best,'holdout':metrics(heldout)},indent=2))
if __name__=='__main__':main()
