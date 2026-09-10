"""Verify READY state through Vercel API and bind deployed content to the ledger.
CLI needs VERCEL_TOKEN. Connected tools may supply independently fetched API
results to make_receipt. Operator-trusted evidence, not independent notarization.
"""
import argparse,json,os,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from publication import snapshot_valid

def make_receipt(deployment,artifact,ledger,now=None):
    if deployment.get('readyState')!='READY' or not deployment.get('id','').startswith('dpl_'):raise ValueError('Verified READY deployment required')
    url=deployment.get('url','')
    if not url or '/' in url or not url.endswith('.vercel.app'):raise ValueError('Unexpected deployment hostname')
    known={s['hash']:s for s in ledger};hashes=[]
    for game in artifact.get('games',[]):
        for snap in game.get('history',[]):
            if not snapshot_valid(snap) or known.get(snap.get('hash'))!=snap:raise ValueError('Published forecast differs from canonical ledger')
            hashes.append(snap['hash'])
    if not hashes:raise ValueError('No verifiable forecasts in deployment')
    at=now or datetime.now(timezone.utc)
    return {'status':'ready','publishedAt':at.isoformat(),'deploymentUrl':'https://'+url,'deploymentId':deployment['id'],'snapshotHashes':sorted(set(hashes))}

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
    root=Path(__file__).resolve().parents[1];ledger=json.loads((root/'data/ledger.json').read_text());receipt=make_receipt(deployment,artifact,ledger)
    path=root/'data/publications.json';receipts=json.loads(path.read_text())
    if any(r['deploymentId']==receipt['deploymentId'] for r in receipts):raise ValueError('Deployment already recorded')
    receipts.append(receipt);path.write_text(json.dumps(receipts,indent=2)+'\n');print(f'Recorded {len(receipt["snapshotHashes"])} verified snapshots')
if __name__=='__main__':main()
