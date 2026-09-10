"""Native Git publication evidence, distinct from direct Vercel API receipts.

Trusts GitHub's authenticated attribution to the installed Vercel bot and an
exact public artifact capture. The production alias is mutable, not notarized.
"""
import hashlib,json,re,subprocess,time,urllib.request
from datetime import datetime,timezone,timedelta
from pathlib import Path
from record_publication import verified_snapshot_hashes
from publication import write_receipts
from publication_preflight import validate_forecast_edition
ROOT=Path(__file__).resolve().parents[1]
REPO='tosterman/nfl-intelligence'
PUBLIC_URL='https://nfl-intelligence-one.vercel.app'

def provider_cooldown(statuses,now):
    candidates=[s for s in statuses if s.get('context')=='Vercel']
    if not candidates:return None
    latest=max(candidates,key=lambda s:s['id'])
    creator=latest.get('creator',{})
    if creator.get('id')!=35613825 or creator.get('login')!='vercel[bot]':raise ValueError('Untrusted Vercel cooldown author')
    if latest.get('state') not in ['failure','error'] or latest.get('target_url')!='https://vercel.com/khnum?upgradeToPro=build-rate-limit':return None
    observed=datetime.fromisoformat(latest['created_at'].replace('Z','+00:00'))
    if observed.tzinfo is None or observed>now:raise ValueError('Invalid provider cooldown time')
    retry_after=observed+timedelta(hours=24)
    return retry_after if now<retry_after else None

def check_provider_cooldown():
    result=subprocess.run(['gh','api',f'repos/{REPO}/commits/main/statuses?per_page=100'],capture_output=True,text=True)
    if result.returncode:raise RuntimeError('Cannot verify production deployment cooldown')
    retry_after=provider_cooldown(json.loads(result.stdout),datetime.now(timezone.utc))
    if retry_after:raise ValueError('Native deployment cooldown remains active until '+retry_after.isoformat()+'; retry eligibility does not guarantee restored capacity')

def verified_status(statuses,now):
    candidates=[s for s in statuses if s.get('context')=='Vercel']
    if not candidates:return None
    latest=max(candidates,key=lambda s:s['id'])
    creator=latest.get('creator',{})
    if creator.get('id')!=35613825 or creator.get('login')!='vercel[bot]':
        raise ValueError('Untrusted Vercel status author')
    if latest['state'] in ['failure','error']:
        if latest.get('target_url')=='https://vercel.com/khnum?upgradeToPro=build-rate-limit':
            raise ValueError('Native deployment blocked by Vercel build rate limit')
        raise ValueError('Native deployment failed')
    if not re.fullmatch(r'https://vercel\.com/khnum/nfl-intelligence/[A-Za-z0-9]+',latest.get('target_url','')):
        raise ValueError('Unexpected Vercel project status URL')
    created=datetime.fromisoformat(latest['created_at'].replace('Z','+00:00'))
    if created.tzinfo is None or created>now:raise ValueError('Invalid provider status time')
    return latest if latest['state']=='success' else None

def make_git_receipt(statuses,sha,artifact,ledger,expected_site,now=None):
    now=now or datetime.now(timezone.utc)
    if not re.fullmatch('[0-9a-f]{40}',sha):raise ValueError('Full source commit required')
    status=verified_status(statuses,now)
    if status is None:raise ValueError('Successful native deployment required')
    hashes=verified_snapshot_hashes(artifact,ledger,expected_site)
    return {'status':'ready','evidenceType':'github-status-and-public-capture',
            'publishedAt':now.isoformat(),'deploymentUrl':PUBLIC_URL,
            'providerDeploymentRef':status['target_url'].rsplit('/',1)[1],
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
    expected=json.loads((ROOT/'data/site.json').read_text());ledger=json.loads((ROOT/'data/ledger.json').read_text())
    validate_forecast_edition(expected,ledger)
    subprocess.run(['git','add','data/player-usage.json','data/personnel-changes.json','data/site.json','data/ledger.json','data/source.json','data/weather.json','data/weather-ledger.json','data/weather-sources/','data/quarterbacks.json','data/quarterback-collection.json','data/quarterback-sources/','data/personnel.json','data/personnel-collection.json','data/personnel-sources/'],check=True)
    changed=subprocess.run(['git','diff','--cached','--quiet']).returncode
    if changed==1:subprocess.run(['git','commit','-m','data: publish refreshed forecast edition'],check=True)
    elif changed!=0:raise RuntimeError('Cannot inspect staged publication')
    sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    recovery=ROOT/'release-recovery';recovery.mkdir(exist_ok=True)
    # Retain intent before the remote mutation, including when push is rejected.
    # This record never proves a successful push, deployment or public capture.
    write_receipts(recovery/'git-publication.json',{'evidenceType':'publication-intent-only','sourceCommit':sha,'repository':REPO,'publicAlias':PUBLIC_URL,'expectedArtifactFile':'data/site.json','canonicalLedgerFile':'data/ledger.json'})
    check_provider_cooldown()
    # Fail closed on concurrent updates; do not silently rebase a tested release.
    subprocess.run(['git','push','origin','HEAD:refs/heads/main'],check=True)
    receipt=capture(sha,expected,ledger)
    path=ROOT/'data/publications.json';receipts=json.loads(path.read_text())
    if not any(r.get('evidenceType')==receipt['evidenceType'] and r.get('sourceCommit')==receipt['sourceCommit'] and r.get('githubStatusId')==receipt['githubStatusId'] for r in receipts):
        receipts.append(receipt);write_receipts(path,receipts)
    print('Verified native Git publication for '+sha+'; '+str(len(receipt['snapshotHashes']))+' snapshots')

if __name__=='__main__':main()
