"""Fixed early/late-2025 quarterback residual experiment; never edits production."""
import hashlib,json
from datetime import datetime,timedelta
from pathlib import Path
import numpy as np
import build_data as base
import experiment_model as efficiency
from refresh import replay_blend
ROOT=Path(__file__).resolve().parents[1]

def difference(home,away):
    if home['status']!='available' or away['status']!='available':return None
    return [home['netYardsPerDropback']-away['netYardsPerDropback'],10*(away['sackRate']-home['sackRate'])]

def fit_adjustment(x,residual,ridge=10):
    # No intercept: swapping teams negates the correction; equal features give zero.
    return np.linalg.solve(x.T@x+ridge*np.eye(2),x.T@residual)

def summary(records,key):
    errors=np.array([r[key]-r['actualMargin'] for r in records])
    return {'games':len(records),'marginMae':float(np.abs(errors).mean()),'marginRmse':float(np.sqrt(np.mean(errors**2)))}

def paired_weeks(records,draws=10000,seed=31025):
    """Resample whole weeks; descriptive uncertainty, not independent-season proof."""
    weeks=sorted({r['week'] for r in records})
    groups=[np.array([abs(r['candidateMargin']-r['actualMargin'])-abs(r['baselineMargin']-r['actualMargin']) for r in records if r['week']==week]) for week in weeks]
    sums=np.array([g.sum() for g in groups]);counts=np.array([len(g) for g in groups])
    sampled=np.random.default_rng(seed).integers(0,len(weeks),size=(draws,len(weeks)))
    deltas=sums[sampled].sum(axis=1)/counts[sampled].sum(axis=1)
    return {'direction':'candidate minus baseline; negative favors candidate','clusters':len(weeks),'draws':draws,'seed':seed,
            'maeDelta':float(sums.sum()/counts.sum()),'percentile95':np.quantile(deltas,[.025,.975]).tolist(),
            'weeks':[{'week':week,'games':len(group),'maeDelta':float(group.mean())} for week,group in zip(weeks,groups)]}

def main():
    site_path=ROOT/'data/site.json';feature_path=ROOT/'reviews/quarterback-feature-audit.json'
    site=json.loads(site_path.read_text());features=json.loads(feature_path.read_text())
    if site['modelVersion']!='score-efficiency-v1.2.0':raise ValueError('Re-specify experiment for changed baseline')
    schedule=ROOT/'data/games.csv'
    if features['scheduleHash']!=hashlib.sha256(schedule.read_bytes()).hexdigest():raise ValueError('Feature schedule changed')
    if not all((ROOT/f'data/raw/stats_team_week_{year}.csv').exists() for year in range(2010,2026)):raise ValueError('Acquire team-stat sources before replay')
    downloads=[efficiency.download(year) for year in range(2010,2026)]
    statmap={(r['game_id'],base.team(r['team'])):efficiency.rates(r) for rows,_ in downloads for r in rows}
    rows=[r for r in base.load_rows(schedule) if r['home_score'] is not None and r['away_score'] is not None and r['season']<=2025]
    baseline,_=replay_blend(rows,statmap)
    schedules={r['game_id']:r for r in rows}
    by_key={(r['gameId'],r['team']):r for r in features['features']}
    if len(by_key)!=len(features['features']):raise ValueError('Duplicate feature scope')
    records=[]
    for game in baseline:
        if game['season']!=2025:continue
        _,_,away,home=game['id'].split('_')
        h=by_key[(game['id'],home)];a=by_key[(game['id'],away)]
        if h['cutoff']!=a['cutoff']:raise ValueError('Mismatched team cutoffs')
        vector=difference(h['form'],a['form'])
        records.append({'gameId':game['id'],'week':game['week'],'cutoff':h['cutoff'],'baselineMargin':game['homeMargin'],
                        'actualMargin':game['actualMargin'],'feature':vector,'split':'fit' if game['week']<=8 else 'evaluate'})
    train=[r for r in records if r['split']=='fit' and r['feature'] is not None]
    evaluate=[r for r in records if r['split']=='evaluate']
    if max(r['cutoff'] for r in train)>=min(r['cutoff'] for r in evaluate):raise ValueError('Chronological split violated')
    last_label_at=max(base.kickoff(schedules[r['gameId']])+timedelta(hours=24) for r in train)
    first_evaluation_at=min(datetime.fromisoformat(r['cutoff']) for r in evaluate)
    if last_label_at>=first_evaluation_at:raise ValueError('Training outcome embargo overlaps evaluation')
    x=np.array([r['feature'] for r in train]);y=np.array([r['actualMargin']-r['baselineMargin'] for r in train])
    coef=fit_adjustment(x,y)
    for r in records:
        r['adjustment']=float(np.array(r['feature'])@coef) if r['feature'] is not None else 0.
        r['candidateMargin']=r['baselineMargin']+r['adjustment']
    comparable=[r for r in evaluate if r['feature'] is not None]
    report={'protocol':'Fixed ridge10, no intercept; net passing rate difference and 10x opposite sack-rate difference. Fit2025weeks1-8; evaluateweek9onward including playoffs. Existing2025development data reused; not untouched holdout.',
            'baselineModelVersion':site['modelVersion'],'baselineReplayScheduleHash':features['scheduleHash'],'teamStatSources':[meta for _,meta in downloads],'featureArtifactHash':hashlib.sha256(feature_path.read_bytes()).hexdigest(),
            'fitGames':len(train),'coefficients':coef.tolist(),'evaluation':{'baseline':summary(evaluate,'baselineMargin'),'candidate':summary(evaluate,'candidateMargin'),'withBothFeatures':len(comparable),'fallbackGames':len(evaluate)-len(comparable)},
            'trainingLabelEmbargoThrough':last_label_at.isoformat(),'firstEvaluationCutoff':first_evaluation_at.isoformat(),
            'codeHashes':{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in ['experiment_quarterback.py','refresh.py','build_data.py','experiment_model.py']},
            'pairedWeeklyUncertainty':paired_weeks(evaluate),
            'comparableEvaluation':{'baseline':summary(comparable,'baselineMargin'),'candidate':summary(comparable,'candidateMargin')},'records':records}
    (ROOT/'reviews/quarterback-experiment-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['records','teamStatSources']},indent=2))
if __name__=='__main__':main()
