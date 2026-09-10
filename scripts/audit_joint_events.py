"""Fixed, overlapping event diagnostics; never modifies production forecasts."""
import hashlib,json
from pathlib import Path
import numpy as np
import build_data as base
from evaluate_joint_scores import priors
from joint_scores import reconcile_scores
from capture_joint_shadow import verify_frozen
from benchmark_uncertainty import compare

ROOT=Path(__file__).resolve().parents[1]

def events(home,away):
    margin=abs(home-away);total=home+away
    return {'margin3':margin==3,'margin7':margin==7,'margin10':margin==10,
            'margin14':margin==14,'margin21plus':margin>=21,
            'total30orless':total<=30,'total60plus':total>=60}

def event_scores(mass,home,away):
    if mass.ndim!=2 or not np.isfinite(mass).all() or (mass<0).any() or abs(mass.sum()-1)>1e-9:
        raise ValueError('Invalid distribution')
    if any(not np.isfinite(x) or x!=int(x) or x<0 or x>=bound for x,bound in zip([home,away],mass.shape)):
        raise ValueError('Outcome outside grid')
    h,a=np.indices(mass.shape);masks=events(h,a);truth=events(home,away)
    result={}
    for name,mask in masks.items():
        probability=float(mass[mask].sum());observed=int(truth[name])
        result[name]={'probability':probability,'observed':observed,'brier':(probability-observed)**2}
    return result

def main():
    source=ROOT/'data/games.csv';site_path=ROOT/'data/site.json'
    raw=site_path.read_bytes();site=json.loads(raw)
    if site['modelVersion']!='score-efficiency-v1.2.0':raise ValueError('Baseline changed')
    empirical,reference,fit=priors(base.load_rows(source))
    frozen=json.loads((ROOT/'reviews/joint-shadow-reference.json').read_text())
    prior_hashes={name:hashlib.sha256(mass.tobytes()).hexdigest() for name,mass in [('candidate',empirical),('reference',reference)]}
    code_hashes={name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in frozen['codeHashes']}
    verify_frozen(frozen,prior_hashes,code_hashes,fit)
    games=[g for g in site['performance']['records'] if g['season']==2025]
    if len(games)!=285 or len({g['id'] for g in games})!=285:raise ValueError('Incomplete sample')
    records=[]
    for g in games:
        home=(g['actualTotal']+g['actualMargin'])/2;away=(g['actualTotal']-g['actualMargin'])/2
        tie=fit['tieProbability'] if g['gameType']=='REG' else 0
        row={'id':g['id'],'season':g['season'],'week':g['week']}
        for name,prior in [('empirical',empirical),('reference',reference)]:
            row[name]=event_scores(reconcile_scores(prior,g['homeScore'],g['awayScore'],tie),home,away)
        records.append(row)
    summary={}
    for event in events(0,0):
        report={}
        for name in ['empirical','reference']:
            rows=[r[name][event] for r in records]
            report[name]={'expectedCount':sum(r['probability'] for r in rows),'observedCount':sum(r['observed'] for r in rows),
                          'meanProbability':float(np.mean([r['probability'] for r in rows])),
                          'observedFrequency':float(np.mean([r['observed'] for r in rows])),
                          'meanBrier':float(np.mean([r['brier'] for r in rows]))}
        paired=compare([{'id':r['id'],'season':r['season'],'week':r['week'],'candidate':r['empirical'][event]['brier'],
                         'reference':r['reference'][event]['brier'],'zero':0} for r in records],'candidate','reference','zero')
        report['pairedBrier']={k:paired[k] for k in ['difference','interval95','clustersBySeason','draws','seed']}
        summary[event]=report
    result={'games':len(records),'numpyVersion':np.__version__,'summary':summary,'records':records,'fit':fit,'priorHashes':prior_hashes,
            'codeHashes':code_hashes|{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in ['audit_joint_events.py','benchmark_uncertainty.py']},
            'siteHash':hashlib.sha256(raw).hexdigest(),'scheduleHash':hashlib.sha256(source.read_bytes()).hexdigest(),
            'protocolHash':hashlib.sha256((ROOT/'reviews/joint-event-audit-protocol.md').read_bytes()).hexdigest(),
            'limitations':'Reused development sample; overlapping events; unadjusted intervals; finite grid; not signed-spread push calibration or production promotion.'}
    (ROOT/'reviews/joint-event-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
