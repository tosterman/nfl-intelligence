"""Verify READY state through Vercel API and bind deployed content to the ledger.
CLI needs VERCEL_TOKEN. Connected tools may supply independently fetched API
results to make_receipt. Operator-trusted evidence, not independent notarization.
"""
import argparse,hashlib,json,os,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from publication import snapshot_valid

def forecast_artifact(site):
    """Exact public /api/forecasts response expected from this release."""
    return {key:site[key] for key in ['generatedAt','modelVersion']} | {'games':[g for g in site['games'] if g.get('snapshot')]}

def wire_json(value):
    """JS JSON serialization drops integral-float spelling; booleans stay distinct."""
    def normalize(item):
        if isinstance(item,dict):return {k:normalize(v) for k,v in item.items()}
        if isinstance(item,list):return [normalize(v) for v in item]
        if isinstance(item,float) and item.is_integer():return int(item)
        return item
    return json.dumps(normalize(value),sort_keys=True,separators=(',',':'),allow_nan=False)

def verified_snapshot_hashes(artifact,ledger,expected_site):
    if wire_json(artifact)!=wire_json(forecast_artifact(expected_site)):raise ValueError('Published artifact differs from intended release')
    known={s['hash']:s for s in ledger};hashes=[]
    for game in artifact.get('games',[]):
        for snap in game.get('history',[]):
            original=known.get(snap.get('hash'))
            if original is None or not snapshot_valid(original) or wire_json(original)!=wire_json(snap):raise ValueError('Published forecast differs from canonical ledger')
            hashes.append(snap['hash'])
    if not hashes:raise ValueError('No verifiable forecasts in deployment')
    return sorted(set(hashes))

def make_receipt(deployment,artifact,ledger,now=None,*,expected_site):
    if deployment.get('readyState')!='READY' or not deployment.get('id','').startswith('dpl_'):raise ValueError('Verified READY deployment required')
    url=deployment.get('url','')
    if not url or '/' in url or not url.endswith('.vercel.app'):raise ValueError('Unexpected deployment hostname')
    hashes=verified_snapshot_hashes(artifact,ledger,expected_site)
    at=now or datetime.now(timezone.utc)
    artifact_hash=hashlib.sha256(json.dumps(artifact,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'status':'ready','publishedAt':at.isoformat(),'deploymentUrl':'https://'+url,'deploymentId':deployment['id'],'snapshotHashes':sorted(set(hashes)),'artifactSha256':artifact_hash}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--deployment-id',required=True);parser.add_argument('--team-id');args=parser.parse_args()
    token=os.environ.get('VERCEL_TOKEN')
    if not token:raise ValueError('VERCEL_TOKEN required to verify deployment')
    if not args.deployment_id.startswith('dpl_'):raise ValueError('Invalid deployment id')
    api='https://api.vercel.com/v13/deployments/'+args.deployment_id+('?teamId='+args.team_id if args.team_id else '')
    request=urllib.request.Request(api,headers={'Authorization':'Bearer '+token})
    deployment=json.load(urllib.request.urlopen(request,timeout=30));url=deployment.get('url','')
    if '/' in url or not url.endswith('.vercel.app'):raise ValueError('Unexpected deployment host')
    artifact=json.load(urllib.request.urlopen('https://'+url+'/api/forecasts',timeout=30))
    root=Path(__file__).resolve().parents[1];ledger=json.loads((root/'data/ledger.json').read_text());expected=json.loads((root/'data/site.json').read_text());receipt=make_receipt(deployment,artifact,ledger,expected_site=expected)
    path=root/'data/publications.json';receipts=json.loads(path.read_text())
    if any(r.get('deploymentId')==receipt['deploymentId'] for r in receipts):raise ValueError('Deployment already recorded')
    receipts.append(receipt);path.write_text(json.dumps(receipts,indent=2)+'\n');print(f'Recorded {len(receipt["snapshotHashes"])} verified snapshots')
if __name__=='__main__':main()
