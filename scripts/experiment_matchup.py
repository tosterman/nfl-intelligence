"""Fixed residual matchup experiment; writes reviews only, never production."""
import hashlib,json
from datetime import timedelta
from pathlib import Path
import numpy as np
import build_data as base
import experiment_model as efficiency
from refresh import replay_blend
from experiment_quarterback import paired_weeks,summary
ROOT=Path(__file__).resolve().parents[1]

def interactions(x):
    # In the existing design, each side contains its offense followed by the
    # opposing defense's allowed rates. Recover those sides from sum/difference.
    home=(x[16:30]+x[2:16])/2;away=(x[16:30]-x[2:16])/2
    return np.array([home[i]*home[i+7]-away[i]*away[i+7] for i in [0,1,3]])

def fit_correction(x,residual):
    scale=np.sqrt(np.mean(x*x,axis=0));scale[scale<1e-8]=1
    normalized=x/scale
    beta=np.linalg.solve(normalized.T@normalized+10*np.eye(3),normalized.T@residual)
    return beta/scale,scale

def main():
    schedule=ROOT/'data/games.csv'
    if not all((ROOT/f'data/raw/stats_team_week_{year}.csv').exists() for year in range(2010,2026)):
        raise ValueError('Acquire source files before this offline experiment')
    downloads=[efficiency.download(year) for year in range(2010,2026)]
    statmap={(r['game_id'],base.team(r['team'])):efficiency.rates(r) for rows,_ in downloads for r in rows}
    rows=[r for r in base.load_rows(schedule) if r['home_score'] is not None and r['away_score'] is not None and r['season']<=2025]
    baseline,_=replay_blend(rows,statmap)
    x,active=efficiency.features(rows,statmap,90)
    by_id={r['game_id']:interactions(v) for r,v in zip(active,x)}
    if len(by_id)!=len(active):raise ValueError('Duplicate game features')
    records=[{'gameId':g['id'],'season':g['season'],'week':g['week'],'feature':by_id[g['id']].tolist(),'actualMargin':g['actualMargin'],'baselineMargin':g['homeMargin']} for g in baseline]
    train=[r for r in records if r['season']==2024];evaluate=[r for r in records if r['season']==2025]
    if len(train)!=285 or len(evaluate)!=285:raise ValueError('Expected complete 2024 and 2025 samples')
    schedules={r['game_id']:r for r in rows}
    last_label=max(base.kickoff(schedules[r['gameId']])+timedelta(hours=24) for r in train)
    first_cutoff=min(schedules[r['gameId']]['gameday'] for r in evaluate)
    if last_label.date().isoformat()>=first_cutoff:raise ValueError('Training label embargo overlaps evaluation')
    beta,scale=fit_correction(np.array([r['feature'] for r in train]),np.array([r['actualMargin']-r['baselineMargin'] for r in train]))
    for r in records:
        r['adjustment']=float(np.array(r['feature'])@beta)
        r['candidateMargin']=r['baselineMargin']+r['adjustment']
    files=['experiment_matchup.py','experiment_quarterback.py','refresh.py','build_data.py','experiment_model.py']
    report={'protocol':'matchup-interaction-protocol.md; fit2024; evaluate2025; development data reused; no production promotion',
        'scheduleHash':hashlib.sha256(schedule.read_bytes()).hexdigest(),'teamStatSources':[meta for _,meta in downloads],
        'codeHashes':{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in files},
        'protocolHash':hashlib.sha256((ROOT/'reviews/matchup-interaction-protocol.md').read_bytes()).hexdigest(),
        'fitGames':len(train),'trainingLabelEmbargoThrough':last_label.isoformat(),'firstEvaluationDate':first_cutoff,
        'featureNames':['passEPA product difference','rushEPA product difference','sackRate product difference'],
        'trainingRms':scale.tolist(),'coefficientsRawUnits':beta.tolist(),
        'evaluation':{'baseline':summary(evaluate,'baselineMargin'),'candidate':summary(evaluate,'candidateMargin')},
        'pairedWeeklyUncertainty':paired_weeks(evaluate),'records':records}
    (ROOT/'reviews/matchup-interaction-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['records','teamStatSources']},indent=2))

if __name__=='__main__':main()
