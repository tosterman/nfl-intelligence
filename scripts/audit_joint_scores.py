"""Feasibility on published forecasts, not an accuracy or betting evaluation."""
import hashlib,json
from pathlib import Path
import numpy as np
import build_data as base
from joint_scores import reconcile_scores
ROOT=Path(__file__).resolve().parents[1]
def main():
    source=ROOT/'data/games.csv';rows=base.load_rows(source)
    historical=[r for r in rows if 2010<=r['season']<=2023 and r['home_score'] is not None and r['away_score'] is not None]
    prior=np.full((101,101),1e-6)
    for r in historical:
        h,a=r['home_score'],r['away_score']
        if h!=int(h) or a!=int(a) or not 0<=h<=100 or not 0<=a<=100:raise ValueError('Historical scores outside declared grid')
        prior[int(h),int(a)]+=.5;prior[int(a),int(h)]+=.5
    regular=[r for r in historical if r['game_type']=='REG'];tie=(1+sum(r['home_score']==r['away_score'] for r in regular))/(100+len(regular))
    path=ROOT/'data/site.json';raw=path.read_bytes();site=json.loads(raw);results=[];h,a=np.indices(prior.shape)
    for game in site['games']:
        if not game['snapshot']:continue
        prediction=game['snapshot']['prediction'];t=tie if game['type']=='REG' else 0
        mass=reconcile_scores(prior,prediction['homeScore'],prediction['awayScore'],t)
        results.append({'gameId':game['id'],'snapshotHash':game['snapshot']['hash'],'homeMean':prediction['homeScore'],'awayMean':prediction['awayScore'],'homeMeanError':float((mass*h).sum()-prediction['homeScore']),'awayMeanError':float((mass*a).sum()-prediction['awayScore']),'tieTarget':t,'tieError':float(np.trace(mass)-t),'sumError':float(mass.sum()-1),'massHash':hashlib.sha256(mass.tobytes()).hexdigest()})
    report={'meaning':'Joint-score mathematical feasibility only. Historical mirrored score counts plus 1e-6 per-cell pseudocount on scores0..100. Fixed historical Beta(1,99) regular-season tie estimate; postseason zero. No conditional football accuracy, tail or key-number calibration claimed; no production writes.',
        'historicalGames':len(historical),'historicalRegularGames':len(regular),'regularTiePrior':tie,'gamesChecked':len(results),'numpyVersion':np.__version__,
        'siteArtifactHash':hashlib.sha256(raw).hexdigest(),'scheduleHash':hashlib.sha256(source.read_bytes()).hexdigest(),'priorHash':hashlib.sha256(prior.tobytes()).hexdigest(),
        'codeHashes':{n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in ['joint_scores.py','audit_joint_scores.py','build_data.py']},'records':results}
    (ROOT/'reviews/joint-score-feasibility.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({**{k:v for k,v in report.items() if k!='records'},'maximumMeanError':max(abs(r[k]) for r in results for k in ['homeMeanError','awayMeanError'])},indent=2))
if __name__=='__main__':main()
