"""Research-only settlement at recorded lines; no executable-price claims."""
import hashlib,json,math
from pathlib import Path
import numpy as np
import build_data as base
from evaluate_joint_scores import priors
from joint_scores import reconcile_scores
from capture_joint_shadow import verify_frozen
from benchmark_uncertainty import compare
ROOT=Path(__file__).resolve().parents[1]

def paired_losses(rows,metric):
    p=compare([{'id':r['id'],'season':r['season'],'week':r['week'],'candidate':r['empirical'][metric],'reference':r['reference'][metric],'zero':0} for r in rows],'candidate','reference','zero')
    return {k:p.get(k) for k in ['difference','interval95','clustersBySeason','draws','seed']}

def settlement(mass,line,actual,market):
    if market not in ['spread','total']:raise ValueError('Unknown market')
    if type(line) not in (int,float) or not math.isfinite(line) or line*2!=int(line*2):raise ValueError('Invalid market line')
    if type(actual) not in (int,float) or not math.isfinite(actual) or actual!=int(actual):raise ValueError('Invalid observed outcome')
    if mass.ndim!=2 or not np.isfinite(mass).all() or (mass<0).any() or abs(mass.sum()-1)>1e-9:raise ValueError('Invalid distribution')
    h,a=np.indices(mass.shape);values=h-a if market=='spread' else h+a
    if not values.min()<=actual<=values.max():raise ValueError('Observed outcome outside grid')
    probabilities=np.array([mass[values>line].sum(),mass[values==line].sum(),mass[values<line].sum()])
    outcome=0 if actual>line else 1 if actual==line else 2
    if probabilities[outcome]<=0:raise ValueError('Zero probability for observed settlement')
    truth=np.zeros(3);truth[outcome]=1
    return {'probabilities':probabilities.tolist(),'outcome':outcome,
            'brier':float(np.sum((probabilities-truth)**2)), 'logLoss':float(-np.log(probabilities[outcome]))}

def main():
    path=ROOT/'data/site.json';raw=path.read_bytes();site=json.loads(raw);source=ROOT/'data/games.csv'
    if site['modelVersion']!='score-efficiency-v1.2.0':raise ValueError('Baseline changed')
    empirical,reference,fit=priors(base.load_rows(source))
    frozen=json.loads((ROOT/'reviews/joint-shadow-reference.json').read_text())
    prior_hashes={n:hashlib.sha256(p.tobytes()).hexdigest() for n,p in [('candidate',empirical),('reference',reference)]}
    code_hashes={n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in frozen['codeHashes']}
    verify_frozen(frozen,prior_hashes,code_hashes,fit)
    games=[g for g in site['performance']['records'] if g['season']==2025]
    if len(games)!=285 or len({g['id'] for g in games})!=285:raise ValueError('Incomplete sample')
    records={'spread':[],'total':[]};missing={'spread':[],'total':[]}
    for g in games:
        tie=fit['tieProbability'] if g['gameType']=='REG' else 0
        distributions={n:reconcile_scores(p,g['homeScore'],g['awayScore'],tie) for n,p in [('empirical',empirical),('reference',reference)]}
        for market,line_key,actual_key in [('spread','marketMargin','actualMargin'),('total','marketTotal','actualTotal')]:
            line=g[line_key]
            if line is None:missing[market].append(g['id']);continue
            row={'id':g['id'],'season':g['season'],'week':g['week'],'line':line,'actual':g[actual_key]}
            for n,mass in distributions.items():row[n]=settlement(mass,line,g[actual_key],market)
            records[market].append(row)
    summary={}
    for market,rows in records.items():
        s={'games':len(rows),'missingLineGameIds':missing[market],'integerLines':sum(r['line']==int(r['line']) for r in rows),'observedPushes':sum(r['empirical']['outcome']==1 for r in rows)}
        s['halfPointLines']=len(rows)-s['integerLines']
        for n in ['empirical','reference']:
            s[n]={'expectedPushes':sum(r[n]['probabilities'][1] for r in rows),**{k:float(np.mean([r[n][k] for r in rows])) if rows else None for k in ['brier','logLoss']}}
        s['paired']={}
        for metric in ['brier','logLoss']:
            s['paired'][metric]=paired_losses(rows,metric)
        summary[market]=s
    report={'summary':summary,'records':records,'fit':fit,'priorHashes':prior_hashes,'numpyVersion':np.__version__,
            'codeHashes':code_hashes|{n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in ['audit_joint_settlement.py','benchmark_uncertainty.py']},
            'siteHash':hashlib.sha256(raw).hexdigest(),'scheduleHash':hashlib.sha256(source.read_bytes()).hexdigest(),
            'protocolHash':hashlib.sha256((ROOT/'reviews/joint-settlement-protocol.md').read_bytes()).hexdigest(),
            'classOrder':{'spread':['homeCover','push','homeLoss'],'total':['over','push','under']},
            'limitations':'Reused development data, recorded closing lines, finite grid, no bookmaker-specific settlement or executable odds; no production promotion.'}
    (ROOT/'reviews/joint-settlement-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
