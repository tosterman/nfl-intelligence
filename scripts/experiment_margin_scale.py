"""One fixed margin calibration diagnostic; no production writes."""
import hashlib,json,math
from datetime import timedelta
from pathlib import Path
import numpy as np
import build_data as base
from benchmark_uncertainty import compare
ROOT=Path(__file__).resolve().parents[1]

def fit_scale(records):
    if not records:raise ValueError('No training records')
    if any(type(r[k]) not in (int,float) or not math.isfinite(r[k]) for r in records for k in ['homeMargin','actualMargin']):raise ValueError('Invalid margin')
    x=np.array([r['homeMargin'] for r in records]);y=np.array([r['actualMargin'] for r in records])
    denom=float(x@x)
    if denom<=0:raise ValueError('Margin scale is not identifiable')
    return max(0.,float(x@y)/denom)

def experiment(records):
    if len({r['id'] for r in records})!=len(records):raise ValueError('Duplicate game identity')
    train=[r for r in records if r['season']==2024];evaluate=[r for r in records if r['season']==2025]
    if not train or not evaluate:raise ValueError('Both seasons required')
    alpha=fit_scale(train)
    rows=[dict(r,candidateMargin=alpha*r['homeMargin']) for r in evaluate]
    result=compare(rows,'candidateMargin','homeMargin','actualMargin')
    result['candidateMae']=result.pop('modelMae');result['baselineMae']=result.pop('marketMae')
    result['candidateRmse']=float(np.sqrt(np.mean([(r['candidateMargin']-r['actualMargin'])**2 for r in rows])))
    result['baselineRmse']=float(np.sqrt(np.mean([(r['homeMargin']-r['actualMargin'])**2 for r in rows])))
    result['records']=[{'id':r['id'],'season':r['season'],'week':r['week'],'actualMargin':r['actualMargin'],'baselineMargin':r['homeMargin'],'candidateMargin':r['candidateMargin']} for r in rows]
    return {'alpha':alpha,'fitGames':len(train),'evaluation':result}

def main():
    path=ROOT/'data/site.json';raw=path.read_bytes();site=json.loads(raw)
    if site['modelVersion']!='score-efficiency-v1.2.0':raise ValueError('Changed baseline requires a new protocol')
    records=site['performance']['records'];schedules=base.load_rows(ROOT/'data/games.csv');by_id={r['game_id']:r for r in schedules}
    if any(sum(r['season']==s for r in records)!=285 for s in [2024,2025]):raise ValueError('Expected complete declared samples')
    last_label=max(base.kickoff(by_id[r['id']])+timedelta(hours=24) for r in records if r['season']==2024)
    first_eval=min(base.kickoff(by_id[r['id']]) for r in records if r['season']==2025)
    if last_label>=first_eval:raise ValueError('Outcome availability overlaps evaluation')
    report=experiment(records)
    report.update(modelVersion=site['modelVersion'],siteArtifactHash=hashlib.sha256(raw).hexdigest(),scheduleHash=hashlib.sha256((ROOT/'data/games.csv').read_bytes()).hexdigest(),
        trainingLabelEmbargoThrough=last_label.isoformat(),firstEvaluationKickoff=first_eval.isoformat(),
        protocolHash=hashlib.sha256((ROOT/'reviews/margin-scale-protocol.md').read_bytes()).hexdigest(),
        codeHashes={n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in ['experiment_margin_scale.py','benchmark_uncertainty.py','build_data.py']},
        limitations='Reused development seasons; current revised inputs; no independent holdout or production promotion. Week resampling does not capture cross-week dependence or model selection uncertainty.')
    market=compare([r for r in records if r['season']==2025],'homeMargin','marketMargin','actualMargin')
    report['closingMarketBenchmark']={k:v for k,v in market.items() if k!='records'}
    (ROOT/'reviews/margin-scale-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({**report,'evaluation':{k:v for k,v in report['evaluation'].items() if k!='records'}},indent=2))
if __name__=='__main__':main()
