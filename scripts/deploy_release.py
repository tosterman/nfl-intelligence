"""Deploy through Vercel REST, wait for READY, verify endpoint, archive receipt."""
import base64,json,os,time,urllib.request
from pathlib import Path
from record_publication import make_receipt
from publication import write_receipts
from publication_preflight import validate_forecast_edition
ROOT=Path(__file__).resolve().parents[1]
ALLOW_ROOT={'package.json','package-lock.json','next.config.ts','tsconfig.json','next-env.d.ts','vercel.json'}
def release_files():
    files=[]
    paths=[p for p in ROOT.iterdir() if p.name in ALLOW_ROOT]
    for folder in ['src','public']:
        paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
    for name in ['site.json','weather.json','weather-venues.json','weather-osm-venues.json',
                 'personnel.json','personnel-collection.json','personnel-changes.json','player-usage.json',
                   'quarterbacks.json','quarterback-collection.json','explosive-plays.json','red-zone.json','source-record-changes.json']:
        paths.append(ROOT/'data'/name)
    for p in paths:
        binary=p.suffix in ['.ttf','.woff','.woff2','.png','.jpg','.ico']
        files.append({'file':p.relative_to(ROOT).as_posix(),'data':base64.b64encode(p.read_bytes()).decode() if binary else p.read_text(encoding='utf-8-sig'),'encoding':'base64' if binary else 'utf-8'})
    return files
def request(path,body=None):
    token=os.environ['VERCEL_TOKEN'];team=os.environ['VERCEL_ORG_ID']
    req=urllib.request.Request('https://api.vercel.com'+path+('?' if '?' not in path else '&')+'teamId='+team,data=json.dumps(body).encode() if body else None,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(req,timeout=60))
def save_recovery_metadata(meta):
    """Keep only public deployment identity; never persist tokens/API secrets."""
    folder=ROOT/'release-recovery';folder.mkdir(exist_ok=True)
    value={key:meta[key] for key in ['id','url','readyState','createdAt','ready'] if key in meta}
    (folder/'deployment.json').write_text(json.dumps(value,indent=2)+'\n')
def main():
    expected=json.loads((ROOT/'data/site.json').read_text())
    ledger=json.loads((ROOT/'data/ledger.json').read_text())
    validate_forecast_edition(expected,ledger)
    result=request('/v13/deployments',{'name':'nfl-intelligence','project':os.environ['VERCEL_PROJECT_ID'],'target':'production','files':release_files(),'projectSettings':{'framework':'nextjs','nodeVersion':'22.x'}})
    save_recovery_metadata(result)
    for _ in range(90):
        meta=request('/v13/deployments/'+result['id'])
        save_recovery_metadata(meta)
        if meta['readyState']=='READY':break
        if meta['readyState'] in ['ERROR','CANCELED']:raise RuntimeError('Deployment failed: '+meta['readyState'])
        time.sleep(5)
    else:raise TimeoutError('Deployment did not become ready')
    url='https://'+meta['url'];artifact=json.load(urllib.request.urlopen(url+'/api/forecasts',timeout=30))
    receipt=make_receipt(meta,artifact,ledger,expected_site=expected)
    path=ROOT/'data/publications.json';receipts=json.loads(path.read_text());receipts.append(receipt);write_receipts(path,receipts)
    print('Verified '+url+'; archived '+str(len(receipt['snapshotHashes']))+' forecast versions')
if __name__=='__main__':main()
