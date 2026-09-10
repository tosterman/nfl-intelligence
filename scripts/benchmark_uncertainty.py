"""Matched-game absolute-error differences with season-stratified week resampling."""
import math
import numpy as np

def compare(records, model_key, market_key, actual_key, draws=10000, seed=20260910):
    if type(draws) is not int or draws < 100: raise ValueError('At least 100 resamples required')
    ids=[r['id'] for r in records]
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate game identity')
    matched=[]
    for r in records:
        if r[market_key] is None: continue
        if any(type(r[k]) not in (int,float) or not math.isfinite(r[k]) for k in [model_key,market_key,actual_key]): raise ValueError('Invalid matched prediction or outcome')
        if type(r['season']) is not int or type(r['week']) is not int: raise ValueError('Invalid week scope')
        model=abs(r[model_key]-r[actual_key]); market=abs(r[market_key]-r[actual_key])
        matched.append({'id':r['id'],'season':r['season'],'week':r['week'],'modelError':model,'marketError':market,'difference':model-market})
    if not matched:return {'games':0,'excludedGames':len(records),'modelMae':None,'marketMae':None,'difference':None,'interval95':None,'records':[]}
    matched.sort(key=lambda r:(r['season'],r['week'],r['id']))
    strata={}
    for r in matched:
        strata.setdefault(r['season'],{}).setdefault(r['week'],[]).append(r['difference'])
    rng=np.random.default_rng(seed);sums=np.zeros(draws);counts=np.zeros(draws)
    for season,weeks in sorted(strata.items()):
        clusters=[weeks[w] for w in sorted(weeks)]
        indexes=rng.integers(0,len(clusters),size=(draws,len(clusters)))
        sums+=np.array([sum(c) for c in clusters])[indexes].sum(axis=1)
        counts+=np.array([len(c) for c in clusters])[indexes].sum(axis=1)
    # Fewer than two clusters in any season cannot estimate within-season variation.
    estimable=all(len(weeks)>=2 for weeks in strata.values())
    return {'games':len(matched),'excludedGames':len(records)-len(matched),
        'modelMae':float(np.mean([r['modelError'] for r in matched])),
        'marketMae':float(np.mean([r['marketError'] for r in matched])),
        'difference':float(np.mean([r['difference'] for r in matched])),
        'interval95':np.quantile(sums/counts,[.025,.975]).tolist() if estimable else None,
        'clustersBySeason':{str(s):len(w) for s,w in sorted(strata.items())},'draws':draws,'seed':seed,'records':matched}
