"""Paired, season-stratified weekly cluster bootstrap of saved experiments.

Descriptive development sensitivity only. Weeks are exchangeable within season;
this does not model cross-week dependence, selection, or parameter uncertainty.
"""
import hashlib,json,re
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def paired_weekly(before,after,seasons,metric='logScore',repetitions=10000,seed=41023):
    if not before.get('sources') or before['sources']!=after.get('sources'):
        raise ValueError('Source identities must match')
    if not before.get('selected') or before['selected']!=after.get('selected'):
        raise ValueError('Selected candidates must match')
    if not isinstance(repetitions,int) or repetitions<100:raise ValueError('At least 100 resamples required')
    def index(report):
        result={}
        for row in report['selectedRecords']:
            game=row['gameId']
            if game in result:raise ValueError('Duplicate game')
            match=re.fullmatch(r'(\d{4})_(\d{2})_[A-Z0-9]+_[A-Z0-9]+',game)
            if not match or int(match[1])!=row['season'] or not 1<=int(match[2])<=30:
                raise ValueError('Invalid game identity or season')
            if not np.isfinite(row[metric]):raise ValueError('Nonfinite score')
            result[game]=row
        return result
    a,b=index(before),index(after)
    if a.keys()!=b.keys():raise ValueError('Paired games must match exactly')
    groups={}
    for game in sorted(a):
        season=a[game]['season']
        if season not in seasons:continue
        week=int(game.split('_')[1]);key=(season,week)
        groups.setdefault(key,[]).append(b[game][metric]-a[game][metric])
    if set(s for s,_ in groups)!=set(seasons):raise ValueError('Requested seasons missing')
    rng=np.random.default_rng(seed);numerator=np.zeros(repetitions);denominator=np.zeros(repetitions)
    for season in sorted(seasons):
        blocks=[v for (s,w),v in sorted(groups.items()) if s==season]
        if len(blocks)<2:raise ValueError('At least two weeks per season required')
        sums=np.array([sum(v) for v in blocks]);counts=np.array([len(v) for v in blocks])
        indices=rng.integers(0,len(blocks),size=(repetitions,len(blocks)))
        numerator+=sums[indices].sum(axis=1);denominator+=counts[indices].sum(axis=1)
    differences=[d for values in groups.values() for d in values]
    return {'metric':metric,'seasons':sorted(seasons),'games':len(differences),'weeks':len(groups),
            'meanDifference':float(np.mean(differences)),
            'interval95':np.quantile(numerator/denominator,[.025,.975]).tolist(),
            'repetitions':repetitions,'seed':seed}

def main():
    paths=[ROOT/f'reviews/distribution-experiment-v{v}-results.json' for v in [2,3]]
    before,after=[json.loads(p.read_text()) for p in paths]
    report={'protocol':__doc__,'direction':'v3 minus v2; negative favors v3 for all reported metrics',
            'inputs':[{'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
            'comparisons':[paired_weekly(before,after,seasons,metric) for seasons in [{2021,2022},{2023}] for metric in ['logScore','crps','outcomeBrier']]}
    path=ROOT/'reviews/distribution-paired-comparison.json'
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
