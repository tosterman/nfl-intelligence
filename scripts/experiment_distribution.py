"""Discrete margin uncertainty research; independent of production artifacts."""
import argparse, json, math
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

def constrain_mean(mass,tie_probability,mean):
    """Fix tie mass and unconditional mean via a support-preserving KL tilt.

    This is a mathematical reconciliation, not an overtime/scoring model.
    Infeasible means fail rather than inventing support or clipping the target.
    """
    mass=np.array(mass,dtype=float,copy=True)
    if mass.shape!=GRID.shape or not np.isfinite(mass).all() or (mass<0).any():
        raise ValueError('Invalid probability mass')
    if not np.isfinite(mean) or not np.isfinite(tie_probability) or not 0<=tie_probability<1:
        raise ValueError('Invalid constraint')
    mass[100]=0
    support=mass>0
    if not support.any():raise ValueError('No nonzero-margin support')
    values=GRID[support];log_weights=np.log(mass[support])
    target=mean/(1-tie_probability)
    if not values.min()<target<values.max():
        raise ValueError('Target mean must lie strictly inside nonzero support')
    def tilted(parameter):
        logs=log_weights+parameter*values
        weights=np.exp(logs-logs.max());weights/=weights.sum()
        return weights
    lower,upper=-1.,1.
    for _ in range(64):
        if float(tilted(lower)@values)<=target<=float(tilted(upper)@values):break
        lower*=2;upper*=2
    else:raise ValueError('Could not bracket target mean')
    for _ in range(100):
        midpoint=(lower+upper)/2
        weights=tilted(midpoint)
        if float(weights@values)<target:lower=midpoint
        else:upper=midpoint
    result=np.zeros_like(mass)
    result[support]=tilted((lower+upper)/2)*(1-tie_probability)
    result[100]=tie_probability
    if abs(float(result@GRID)-mean)>1e-9:raise ValueError('Mean reconciliation failed')
    return result

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

def evaluate(records,method,settlement=False,mean_preserving=False):
    out=[]
    for p in records:
        r=p['row']
        if r['season']<2021:continue
        residuals=[q['row']['home_score']-q['row']['away_score']-q['margin'] for q in records if q['row']['gameday']<p['cutoff']]
        pmf=distribution(p['margin'],residuals,method)
        if mean_preserving:
            pmf=constrain_mean(pmf,prior_tie_probability(records,p['cutoff'],r.get('game_type','REG')),p['margin'])
        elif settlement:pmf=settlement_constrain(pmf,prior_tie_probability(records,p['cutoff'],r.get('game_type','REG')))
        out.append({'gameId':r['game_id'],'season':r['season'],'meanError':float(pmf@GRID)-p['margin'],**measure(pmf,r['home_score']-r['away_score'])})
    return out

def aggregate(records,seasons):
    pp=[p for p in records if p['season'] in seasons]
    return {'games':len(pp),**{k:float(np.mean([p[k] for p in pp])) for k in ['logScore','crps','coverage80','width80','tieProbability','outcomeBrier']},'expectedTies':float(sum(p['tieProbability'] for p in pp)),'actualTies':int(sum(p['actualTie'] for p in pp)),'maxAbsoluteMeanError':float(max(abs(p['meanError']) for p in pp))}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mean-preserving',action='store_true');args=parser.parse_args()
    rows=[r for r in base.load_rows(model.ROOT/'data/games.csv') if r['home_score'] is not None and r['away_score'] is not None and r['season']<=2023]
    downloads=[model.download(s) for s in range(2010,2024)]
    stats={(r['game_id'],base.team(r['team'])):model.rates(r) for records,_ in downloads for r in records}
    records=rest.baseline_replay(rows,stats)
    predictions={m:evaluate(records,m,settlement=True,mean_preserving=args.mean_preserving) for m in METHODS}
    validation={m:aggregate(p,[2021,2022]) for m,p in predictions.items()}
    selected=min(METHODS,key=lambda m:validation[m]['logScore'])
    report={'protocol':'Settlement constraint v2: postseason zero tie; regular-season Beta(1,99) posterior from eligible prior-week2017+ REG results only. Fixed candidates, choose discrete log score2021-22, separate2023; no2024-25. Nonzero margin probabilities renormalized proportionally, not an overtime simulator.','validation':validation,'selected':selected,'validation2023':{m:aggregate(predictions[m],[2023]) for m in ['normal14',selected]},'selectedRecords':predictions[selected],'sources':[s for _,s in downloads]}
    version='v3' if args.mean_preserving else 'v2'
    if args.mean_preserving:
        report['protocol']='Mean-preserving v3: fixed prior-only REG tie posterior, zero POST tie; exponential tilt of positive nonzero support to preserve unconditional model mean. Select log score2021-22; 2023 reused development diagnostic, not an untouched validation set. No2024-25.'
    (model.ROOT/f'reviews/distribution-experiment-{version}-results.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ['selectedRecords','sources']},indent=2))

if __name__=='__main__':main()
