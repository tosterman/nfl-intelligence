"""Native Git publication evidence, distinct from direct Vercel API receipts.

Trusts GitHub's authenticated attribution to the installed Vercel bot and an
exact public artifact capture. The production alias is mutable, not notarized.
"""
import hashlib,json,re,subprocess,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from record_publication import verified_snapshot_hashes
ROOT=Path(__file__).resolve().parents[1]
REPO='tosterman/nfl-intelligence'
PUBLIC_URL='https://nfl-intelligence-one.vercel.app'

def verified_status(statuses,now):
    candidates=[s for s in statuses if s.get('context')=='Vercel']
    if not candidates:return None
    latest=max(candidates,key=lambda s:s['id'])
    creator=latest.get('creator',{})
    if creator.get('id')!=35613825 or creator.get('login')!='vercel[bot]':
        raise ValueError('Untrusted Vercel status author')
    if not re.fullmatch(r'https://vercel\.com/khnum/nfl-intelligence/[A-Za-z0-9]+',latest.get('target_url','')):
        raise ValueError('Unexpected Vercel project status URL')
    created=datetime.fromisoformat(latest['created_at'].replace('Z','+00:00'))
    if created.tzinfo is None or created>now:raise ValueError('Invalid provider status time')
    if latest['state'] in ['failure','error']:raise ValueError('Native deployment failed')
    return latest if latest['state']=='success' else None

def make_git_receipt(statuses,sha,artifact,ledger,expected_site,now=None):
    now=now or datetime.now(timezone.utc)
    if not re.fullmatch('[0-9a-f]{40}',sha):raise ValueError('Full source commit required')
    status=verified_status(statuses,now)
    if status is None:raise ValueError('Successful native deployment required')
    hashes=verified_snapshot_hashes(artifact,ledger,expected_site)
    return {'status':'ready','evidenceType':'github-status-and-public-capture',
            'publishedAt':now.isoformat(),'deploymentUrl':PUBLIC_URL,
            'deploymentId':'dpl_'+status['target_url'].rsplit('/',1)[1],
            'deploymentInspectorUrl':status['target_url'],'sourceCommit':sha,
            'repository':REPO,'githubStatusId':status['id'],'providerStatusAt':status['created_at'],
            'snapshotHashes':hashes,'artifactSha256':hashlib.sha256(json.dumps(artifact,sort_keys=True,separators=(',',':')).encode()).hexdigest()}

def capture(sha,expected,ledger,timeout=600):
    if not re.fullmatch('[0-9a-f]{40}',sha):raise ValueError('Full source commit required')
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        result=subprocess.run(['gh','api',f'repos/{REPO}/commits/{sha}/statuses?per_page=100'],capture_output=True,text=True)
        if result.returncode:raise RuntimeError('GitHub deployment status lookup failed')
        statuses=json.loads(result.stdout)
        status=verified_status(statuses,datetime.now(timezone.utc))
        if status:
            request=urllib.request.Request(PUBLIC_URL+'/api/forecasts?release='+sha,headers={'Cache-Control':'no-cache'})
            try:
                with urllib.request.urlopen(request,timeout=30) as response:
                    if response.geturl().split('/api/')[0]!=PUBLIC_URL:raise ValueError('Unexpected public redirect')
                    artifact=json.load(response)
                return make_git_receipt(statuses,sha,artifact,ledger,expected)
            except (OSError,ValueError):
                pass # Alias propagation may trail status; never archive mismatched bytes.
        time.sleep(10)
    raise TimeoutError('Native deployment/public artifact not verified within ten minutes')

def main():
    branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip()
    if branch!='main':raise ValueError('Native publication requires main checkout')
    subprocess.run(['git','add','data/site.json','data/ledger.json','data/source.json','data/weather.json','data/weather-ledger.json','data/weather-sources/'],check=True)
    changed=subprocess.run(['git','diff','--cached','--quiet']).returncode
    if changed==1:subprocess.run(['git','commit','-m','data: publish refreshed forecast edition'],check=True)
    elif changed!=0:raise RuntimeError('Cannot inspect staged publication')
    # Fail closed on concurrent updates; do not silently rebase a tested release.
    subprocess.run(['git','push','origin','HEAD:refs/heads/main'],check=True)
    sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    expected=json.loads((ROOT/'data/site.json').read_text());ledger=json.loads((ROOT/'data/ledger.json').read_text())
    recovery=ROOT/'release-recovery';recovery.mkdir(exist_ok=True)
    (recovery/'git-publication.json').write_text(json.dumps({'sourceCommit':sha,'repository':REPO,'publicAlias':PUBLIC_URL,'expectedArtifactFile':'data/site.json','canonicalLedgerFile':'data/ledger.json'},indent=2)+'\n')
    receipt=capture(sha,expected,ledger)
    path=ROOT/'data/publications.json';receipts=json.loads(path.read_text())
    if not any(r.get('deploymentId')==receipt['deploymentId'] for r in receipts):
        receipts.append(receipt);path.write_text(json.dumps(receipts,indent=2)+'\n')
    print('Verified native Git publication for '+sha+'; '+str(len(receipt['snapshotHashes']))+' snapshots')

if __name__=='__main__':main()
