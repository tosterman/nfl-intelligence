"""Frozen joint-score comparison. Research artifacts only."""
import hashlib,json,math
from pathlib import Path
import numpy as np
import build_data as base
from joint_scores import reconcile_scores
from benchmark_uncertainty import compare
ROOT=Path(__file__).resolve().parents[1]

def priors(rows,size=101):
    counts=np.zeros((size,size));regular=ties=0
    for r in rows:
        if not 2010<=r['season']<=2023:continue
        h,a=r['home_score'],r['away_score']
        if h is None or a is None:continue
        if not all(math.isfinite(x) and x==int(x) and 0<=x<size for x in [h,a]):raise ValueError('Invalid historical score')
        counts[int(h),int(a)]+=.5;counts[int(a),int(h)]+=.5
        if r['game_type']=='REG':regular+=1;ties+=h==a
    n=counts.sum()
    if n<2 or regular<1:raise ValueError('Insufficient prior history')
    marginal=counts.sum(axis=1)+1;marginal/=marginal.sum()
    empirical=counts+100*np.outer(marginal,marginal);empirical/=empirical.sum()
    h,a=np.indices(counts.shape);x=np.stack([h.ravel(),a.ravel()],axis=1)
    w=counts.ravel()/n;mu=w@x;centered=x-mu;cov=centered.T@(centered*w[:,None])
    if np.linalg.eigvalsh(cov).min()<=0:raise ValueError('Degenerate reference covariance')
    logs=-.5*np.einsum('ij,jk,ik->i',centered,np.linalg.inv(cov),centered)
    gaussian=np.exp(logs-logs.max()).reshape(counts.shape);gaussian/=gaussian.sum()
    return empirical,gaussian,{'games':int(n),'regularGames':regular,'tieProbability':(ties+1)/(regular+100),'referenceMean':mu.tolist(),'referenceCovariance':cov.tolist()}

def score(mass,home,away):
    if home!=int(home) or away!=int(away) or not 0<=home<mass.shape[0] or not 0<=away<mass.shape[1]:raise ValueError('Outcome outside grid')
    if not np.isfinite(mass).all() or (mass<0).any() or abs(mass.sum()-1)>1e-9:raise ValueError('Invalid distribution')
    h,a=np.indices(mass.shape);offset=mass.shape[1]-1
    margin=np.bincount((h-a+offset).ravel(),weights=mass.ravel(),minlength=sum(mass.shape)-1)
    total=np.bincount((h+a).ravel(),weights=mass.ravel(),minlength=sum(mass.shape)-1)
    actual_margin=int(home-away+offset);actual_total=int(home+away)
    probabilities=[mass[int(home),int(away)],margin[actual_margin],total[actual_total]]
    if min(probabilities)<=0:raise ValueError('Zero probability for observed outcome')
    event=np.array([mass[h<a].sum(),mass[h==a].sum(),mass[h>a].sum()]);truth=np.array([home<away,home==away,home>away],dtype=float)
    return {'jointLogScore':float(-np.log(probabilities[0])),'marginLogScore':float(-np.log(probabilities[1])),'totalLogScore':float(-np.log(probabilities[2])),
        'marginCrps':float(np.sum((np.cumsum(margin)[:-1]-(np.arange(len(margin)-1)>=actual_margin))**2)),
        'totalCrps':float(np.sum((np.cumsum(total)[:-1]-(np.arange(len(total)-1)>=actual_total))**2)),
        'threeOutcomeBrier':float(np.sum((event-truth)**2)),'tieProbability':float(event[1])}

def main():
    source=ROOT/'data/games.csv';historical=base.load_rows(source);empirical,gaussian,fit=priors(historical)
    path=ROOT/'data/site.json';raw=path.read_bytes();site=json.loads(raw)
    if site['modelVersion']!='score-efficiency-v1.2.0':raise ValueError('Changed baseline requires new protocol')
    games=[r for r in site['performance']['records'] if r['season']==2025]
    if len(games)!=285 or len({r['id'] for r in games})!=285:raise ValueError('Expected complete evaluation sample')
    records=[];max_error=0.;h,a=np.indices(empirical.shape)
    for g in games:
        home=(g['actualTotal']+g['actualMargin'])/2;away=(g['actualTotal']-g['actualMargin'])/2
        tie=fit['tieProbability'] if g['gameType']=='REG' else 0
        record={'id':g['id'],'season':g['season'],'week':g['week'],'phase':g['gameType'],'actualHome':home,'actualAway':away}
        for name,prior in [('empirical',empirical),('reference',gaussian)]:
            mass=reconcile_scores(prior,g['homeScore'],g['awayScore'],tie)
            max_error=max(max_error,abs(float((mass*h).sum())-g['homeScore']),abs(float((mass*a).sum())-g['awayScore']))
            record[name]=score(mass,home,away)
        records.append(record)
    keys=list(records[0]['empirical']);summary={name:{k:float(np.mean([r[name][k] for r in records])) for k in keys} for name in ['empirical','reference']}
    paired=compare([{'id':r['id'],'season':r['season'],'week':r['week'],'candidate':r['empirical']['jointLogScore'],'reference':r['reference']['jointLogScore'],'zero':0} for r in records],'candidate','reference','zero')
    uncertainty={k:paired[k] for k in ['difference','interval95','clustersBySeason','draws','seed']}
    report={'protocolHash':hashlib.sha256((ROOT/'reviews/joint-score-evaluation-protocol.md').read_bytes()).hexdigest(),'modelVersion':site['modelVersion'],
        'siteArtifactHash':hashlib.sha256(raw).hexdigest(),'scheduleHash':hashlib.sha256(source.read_bytes()).hexdigest(),'numpyVersion':np.__version__,
        'codeHashes':{n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in ['evaluate_joint_scores.py','joint_scores.py','benchmark_uncertainty.py','build_data.py']},
        'fit':fit,'games':len(records),'summary':summary,'pairedJointLogScore':uncertainty,'maximumMeanError':max_error,
        'expectedTies':sum(r['empirical']['tieProbability'] for r in records),'observedTies':sum(r['actualHome']==r['actualAway'] for r in records),
        'limitations':'Reused development data, finite score grid, historical mixed-era shape and tie prior. Not a comparison with the continuous production normal or a calibrated betting simulator. No production promotion.', 'records':records}
    (ROOT/'reviews/joint-score-evaluation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
if __name__=='__main__':main()
