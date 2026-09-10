"""Descriptive 80% interval audit; no fitting, optimization or significance test."""
import math
import hashlib,json
from pathlib import Path

def summarize(records, interval_key, actual_key):
    covered=below=above=0
    widths=[];scores=[];missed=[];seen=set()
    for r in records:
        if not r.get('id') or r['id'] in seen:raise ValueError('Invalid or duplicate game identity')
        seen.add(r['id'])
        bounds=r[interval_key];actual=r[actual_key]
        if not isinstance(bounds,list) or len(bounds)!=2:raise ValueError('Interval requires two bounds')
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in [*bounds,actual]):raise ValueError('Invalid interval or outcome')
        lo,hi=bounds
        if lo>hi:raise ValueError('Reversed interval')
        widths.append(hi-lo)
        # Central 80% interval score: width plus 2/alpha times miss distance.
        scores.append(hi-lo+10*max(lo-actual,actual-hi,0))
        if actual<lo:below+=1;missed.append(r['id'])
        elif actual>hi:above+=1;missed.append(r['id'])
        else:covered+=1
    n=len(records)
    return {'games':n,'covered':covered,'below':below,'above':above,
            'coverage':covered/n if n else None,
            'meanWidth':sum(widths)/n if n else None,
            'meanIntervalScore':sum(scores)/n if n else None,
            'missedGameIds':missed}

def audit(records):
    for r in records:
        p=r['homeWinProbability'];market=r['marketMargin'];margin=r['homeMargin']
        if type(p) not in (int,float) or not math.isfinite(p) or not 0<=p<=1:raise ValueError('Invalid probability')
        if type(margin) not in (int,float) or not math.isfinite(margin):raise ValueError('Invalid model margin')
        if market is not None and (type(market) not in (int,float) or not math.isfinite(market)):raise ValueError('Invalid market margin')
    def both(group):return {'margin':summarize(group,'marginInterval80','actualMargin'),'total':summarize(group,'totalInterval80','actualTotal')}
    return {'all':both(records),
      'confidence':[{'lower':lo,'upper':min(hi,1),'upperInclusive':hi>1,**both([r for r in records if lo<=max(r['homeWinProbability'],1-r['homeWinProbability'])<hi])} for lo,hi in [(.5,.6),(.6,.7),(.7,.8),(.8,1.01)]],
      'disagreement':[{'lower':lo,'upper':hi,**both([r for r in records if r['marketMargin'] is not None and lo<=abs(r['homeMargin']-r['marketMargin']) and (hi is None or abs(r['homeMargin']-r['marketMargin'])<hi)])} for lo,hi in [(0,2),(2,4),(4,6),(6,None)]],
      'missingMarketGames':sum(r['marketMargin'] is None for r in records)}

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    raw=(root/'data/site.json').read_bytes();site=json.loads(raw)
    report={'sourceSha256':hashlib.sha256(raw).hexdigest(),'editionGeneratedAt':site['generatedAt'],
      'scope':'Retrospective development records; fixed descriptive bands, not independent holdout or prospective evidence. No significance testing or model adjustment.',
      'nominalCoverage':.8,'intervalScoreMeaning':'Width plus 10 times outside distance; lower is better. Includes interval endpoints.',
      **audit(site['performance']['records'])}
    (root/'reviews/interval-diagnostics.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:([{ 'lower':r['lower'],'games':r['margin']['games'],'marginCoverage':r['margin']['coverage'],'totalCoverage':r['total']['coverage']} for r in report[key]] if key!='all' else report[key]) for key in ['all','confidence','disagreement']}))
