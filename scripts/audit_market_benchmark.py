"""Audit the exact published historical record; no refit or production mutation."""
import hashlib,json
from pathlib import Path
from benchmark_uncertainty import compare
ROOT=Path(__file__).resolve().parents[1]
def main():
    path=ROOT/'data/site.json';raw=path.read_bytes();site=json.loads(raw)
    records=site['performance']['records']
    report={'siteArtifactHash':hashlib.sha256(raw).hexdigest(),'modelVersion':site['modelVersion'],'generatedAt':site['generatedAt'],
        'method':'Paired absolute-error difference (model minus market), matched games only; sample whole season/week clusters with replacement within each season, pooling game-weighted errors. 10000 percentile resamples, fixed seed20260910.',
        'limitations':'Reused historical development data and revised closing lines. Not prospective or profitable-edge evidence. Weeks are treated as independent within season; cross-week team dependence and model-selection uncertainty are not captured. Intervals are descriptive, not causal.',
        'codeHashes':{n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in ['audit_market_benchmark.py','benchmark_uncertainty.py']},
        'spread':compare(records,'homeMargin','marketMargin','actualMargin'),
        'total':compare(records,'total','marketTotal','actualTotal')}
    (ROOT/'reviews/market-benchmark-uncertainty.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:({a:b for a,b in v.items() if a!='records'} if k in ['spread','total'] else v) for k,v in report.items()},indent=2))
if __name__=='__main__':main()
