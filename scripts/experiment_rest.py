"""Bounded rest correction research; never writes production model/artifacts."""
import json
from datetime import datetime
import numpy as np
import build_data as base
import experiment_model as model

def week_key(r):return (r['season'],r['week'],r['game_type'])

def rest_evidence(row,history,cutoff,cap=14):
    """Only prior same-season completed dates strictly before weekly cutoff.

    None means no qualifying history; correction must abstain. Stored schedule
    home_rest/away_rest fields are deliberately ignored.
    """
    dates={}
    for side in ['home','away']:
        team=row[side+'_team']
        prior=[r['gameday'] for r in history if r['season']==row['season'] and r['gameday']<cutoff and r['gameday']<row['gameday'] and team in (r['home_team'],r['away_team']) and r['home_score'] is not None and r['away_score'] is not None]
        dates[side]=max(prior) if prior else None
    days={side:(datetime.fromisoformat(row['gameday'])-datetime.fromisoformat(date)).days if date else None for side,date in dates.items()}
    diff=min(days['home'],cap)-min(days['away'],cap) if all(d is not None for d in days.values()) else None
    return {'homePreviousGame':dates['home'],'awayPreviousGame':dates['away'],'homeRestDays':days['home'],'awayRestDays':days['away'],'difference':diff,'cutoff':cutoff,'capDays':cap}

def fit_rest(feature,residual,ridge):
    """No intercept: zero rest difference must give zero adjustment."""
    denom=float(feature@feature)+ridge
    return float(feature@residual)/denom if denom>0 else 0.

def baseline_replay(rows,statmap):
    x,active=model.features(rows,statmap,90)
    result=[];cache={}
    for i,r in enumerate(active):
        if not 2017<=r['season']<=2023:continue
        key=week_key(r)
        if key not in cache:
            cutoff=min(g['gameday'] for g in active if week_key(g)==key)
            tr=np.array([g['gameday']<cutoff for g in active])
            y=np.array([[g['home_score']-g['away_score'],g['home_score']+g['away_score']] for g,ok in zip(active,tr) if ok])
            cache[key]=(model.fit_symmetric(x[tr],y,10),base.fit(rows,cutoff,180,6)[0],cutoff)
        epa,score,cutoff=cache[key];ep=x[i]@epa;sc=base.predict(score,r)
        result.append({'row':r,'cutoff':cutoff,'margin':.75*sc['homeMargin']+.25*float(ep[0]),'total':.75*sc['total']+.25*float(ep[1])})
    return result

def corrected(records,rows,cap,ridge):
    features=np.array([rest_evidence(p['row'],rows,p['cutoff'],cap)['difference'] or 0 for p in records],dtype=float)
    residual=np.array([p['row']['home_score']-p['row']['away_score']-p['margin'] for p in records])
    output=[]
    for i,p in enumerate(records):
        r=p['row']
        if r['season']<2021:continue
        tr=np.array([q['row']['gameday']<p['cutoff'] for q in records])
        coefficient=fit_rest(features[tr],residual[tr],ridge)
        output.append({'gameId':r['game_id'],'season':r['season'],'margin':p['margin']+coefficient*features[i],'total':p['total'],'adjustment':coefficient*features[i],'coefficient':coefficient,'feature':features[i],'actualMargin':r['home_score']-r['away_score'],'actualTotal':r['home_score']+r['away_score']})
    return output

def metrics(records,seasons):
    pp=[p for p in records if p['season'] in seasons]
    pred=np.array([[p['margin'],p['total']] for p in pp]);y=np.array([[p['actualMargin'],p['actualTotal']] for p in pp])
    return model.summarize(pred,y,np.array([14,14]))

def main():
    # No 2024-25 evaluation or fitting in this experiment.
    rows=[r for r in base.load_rows(model.ROOT/'data/games.csv') if r['home_score'] is not None and r['away_score'] is not None and r['season']<=2023]
    downloads=[model.download(s) for s in range(2010,2024)]
    sm={(r['game_id'],base.team(r['team'])):model.rates(r) for records,_ in downloads for r in records}
    baseline=baseline_replay(rows,sm)
    none=[{'gameId':p['row']['game_id'],'season':p['row']['season'],'margin':p['margin'],'total':p['total'],'actualMargin':p['row']['home_score']-p['row']['away_score'],'actualTotal':p['row']['home_score']+p['row']['away_score']} for p in baseline if p['row']['season']>=2021]
    candidates=[{'name':'no rest','validation':metrics(none,[2021,2022])}];preds={'no rest':none}
    for cap in [14,21]:
        for ridge in [0,100,1000]:
            pred=corrected(baseline,rows,cap,ridge);name=f'cap{cap}-ridge{ridge}'
            candidates.append({'name':name,'cap':cap,'ridge':ridge,'validation':metrics(pred,[2021,2022])});preds[name]=pred
    chosen=min(candidates,key=lambda c:c['validation']['margin_mae'])
    challenger=min(candidates[1:],key=lambda c:c['validation']['margin_mae'])
    report={'protocol':'Select 2021-22 margin MAE, separate 2023 check; 2024-25 excluded. Fixed symmetric blend foundation already selected on 2021-22. No confidence claim from reused validation.','candidates':candidates,'selected':chosen,'bestRestChallenger':challenger,'validation2023':{name:metrics(preds[name],[2023]) for name in ['no rest',challenger['name']]},'selectedRecords':preds[chosen['name']],'challengerRecords':preds[challenger['name']],'sources':[s for _,s in downloads]}
    (model.ROOT/'reviews/rest-experiment-results.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ['selectedRecords','challengerRecords','sources']},indent=2))

if __name__=='__main__':main()
