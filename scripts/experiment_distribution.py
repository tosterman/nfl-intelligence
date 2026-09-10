"""Discrete margin uncertainty research; independent of production artifacts."""
import json, math
import numpy as np
import build_data as base
import experiment_model as model
import experiment_rest as rest

GRID=np.arange(-100,101,dtype=float)
METHODS=['normal14','normal_fitted','empirical_bw1','empirical_bw2','empirical_bw4']

def ndtr(values):
    """Normal CDF using Python's libm erf; no SciPy runtime dependency."""
    values=np.asarray(values,dtype=float)
    return .5*(1+np.frompyfunc(math.erf,1,1)(values/math.sqrt(2)).astype(float))

def prior_tie_probability(records,cutoff,game_type):
    """Prespecified Beta(1,99): 1% mean, 100 pseudo-games; REG only.

    Eligible observed games strictly precede the current weekly cutoff. No
    pooling of postseason ties, no fitting the prior on validation outcomes.
    """
    if game_type!='REG':return 0.
    eligible=[p['row'] for p in records if p['row']['gameday']<cutoff and p['row'].get('game_type','REG')=='REG' and p['row']['home_score'] is not None and p['row']['away_score'] is not None]
    ties=sum(r['home_score']==r['away_score'] for r in eligible)
    return (ties+1)/(len(eligible)+100)

def settlement_constrain(mass,tie_probability):
    if not 0<=tie_probability<1:raise ValueError('Invalid tie probability')
    adjusted=np.array(mass,dtype=float,copy=True);adjusted[100]=0
    weight=adjusted.sum()
    if weight<=0:raise ValueError('No nonzero-margin mass')
    adjusted*=((1-tie_probability)/weight);adjusted[100]=tie_probability
    return adjusted

def distribution(mean,residuals,method):
    """Symmetric residual law centered on mean, integrated into integer bins.

    End bins include tail overflow; this is numerical support, not score rules.
    Symmetrization is structural and does not establish football key-number fit.
    """
    residuals=np.asarray(residuals,dtype=float)
    if len(residuals)<100:raise ValueError('At least 100 prior out-of-sample residuals required')
    edges=GRID[:-1]+.5
    if method=='normal14':cdf=ndtr((edges-mean)/14.)
    elif method=='normal_fitted':
        sigma=max(1.,float(np.sqrt(np.mean(residuals**2))))
        cdf=ndtr((edges-mean)/sigma)
    elif method.startswith('empirical_bw'):
        bw=float(method.split('bw')[1])
        if bw<=0:raise ValueError('Positive bandwidth required')
        bins=np.clip(np.rint(np.r_[residuals,-residuals]),-100,100).astype(int)+100
        weights=np.bincount(bins,minlength=201).astype(float);weights/=weights.sum()
        cdf=ndtr((edges[:,None]-mean-GRID[None,:])/bw)@weights
    else:raise ValueError('Unknown method')
    mass=np.diff(np.r_[0.,cdf,1.]);mass=np.maximum(0,mass);mass/=mass.sum()
    return mass

def measure(mass,actual):
    if not -100<=actual<=100 or int(actual)!=actual:raise ValueError('Unsupported outcome')
    idx=int(actual)+100;cdf=np.cumsum(mass);indicator=(GRID>=actual).astype(float)
    lo=float(GRID[np.searchsorted(cdf,.1)]);hi=float(GRID[np.searchsorted(cdf,.9)])
    outcome=np.array([mass[:100].sum(),mass[100],mass[101:].sum()])
    observed=np.array([float(actual<0),float(actual==0),float(actual>0)])
    return {'logScore':float(-np.log(max(mass[idx],1e-15))),'crps':float(np.sum((cdf-indicator)**2)),'coverage80':float(lo<=actual<=hi),'width80':hi-lo,'tieProbability':float(mass[100]),'actualTie':float(actual==0),'outcomeBrier':float(np.sum((outcome-observed)**2))}

def evaluate(records,method,settlement=False):
    out=[]
    for p in records:
        r=p['row']
        if r['season']<2021:continue
        residuals=[q['row']['home_score']-q['row']['away_score']-q['margin'] for q in records if q['row']['gameday']<p['cutoff']]
        pmf=distribution(p['margin'],residuals,method)
        if settlement:pmf=settlement_constrain(pmf,prior_tie_probability(records,p['cutoff'],r.get('game_type','REG')))
        out.append({'gameId':r['game_id'],'season':r['season'],**measure(pmf,r['home_score']-r['away_score'])})
    return out

def aggregate(records,seasons):
    pp=[p for p in records if p['season'] in seasons]
    return {'games':len(pp),**{k:float(np.mean([p[k] for p in pp])) for k in ['logScore','crps','coverage80','width80','tieProbability','outcomeBrier']},'expectedTies':float(sum(p['tieProbability'] for p in pp)),'actualTies':int(sum(p['actualTie'] for p in pp))}

def main():
    rows=[r for r in base.load_rows(model.ROOT/'data/games.csv') if r['home_score'] is not None and r['away_score'] is not None and r['season']<=2023]
    downloads=[model.download(s) for s in range(2010,2024)]
    stats={(r['game_id'],base.team(r['team'])):model.rates(r) for records,_ in downloads for r in records}
    records=rest.baseline_replay(rows,stats)
    predictions={m:evaluate(records,m,settlement=True) for m in METHODS}
    validation={m:aggregate(p,[2021,2022]) for m,p in predictions.items()}
    selected=min(METHODS,key=lambda m:validation[m]['logScore'])
    report={'protocol':'Settlement constraint v2: postseason zero tie; regular-season Beta(1,99) posterior from eligible prior-week2017+ REG results only. Fixed candidates, choose discrete log score2021-22, separate2023; no2024-25. Nonzero margin probabilities renormalized proportionally, not an overtime simulator.','validation':validation,'selected':selected,'validation2023':{m:aggregate(predictions[m],[2023]) for m in ['normal14',selected]},'selectedRecords':predictions[selected],'sources':[s for _,s in downloads]}
    (model.ROOT/'reviews/distribution-experiment-v2-results.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ['selectedRecords','sources']},indent=2))

if __name__=='__main__':main()
