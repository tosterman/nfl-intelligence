"""Verify the selected personnel publication through public health endpoints."""
import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main(url):
    publication=json.loads((ROOT/'reviews/personnel-incremental-publication.json').read_bytes())
    if publication['mode']!='published':raise ValueError('Actual publication required')
    expected=publication['publication']['sha256']
    deadline=time.monotonic()+120
    attempts=[]
    while True:
        checks=[]
        for endpoint in ('personnel-status','quarterback-status','participation-status'):
            try:
                try:response=urllib.request.urlopen(url.rstrip('/')+'/api/'+endpoint,timeout=15)
                except urllib.error.HTTPError as error:response=error
                with response:
                    raw=response.read(100_001)
                    if len(raw)>100_000:raise ValueError('Unexpected personnel health response size')
                    body=json.loads(raw)
                    if not isinstance(body,dict):raise ValueError('Unexpected health body')
                    checks.append({'endpoint':endpoint,'httpStatus':response.status,'body':body})
            except (urllib.error.URLError,TimeoutError,OSError,ValueError) as error:
                checks.append({'endpoint':endpoint,'httpStatus':None,'body':{},'errorType':type(error).__name__})
        attempts.append({'checkedAt':datetime.now(timezone.utc).isoformat(),'checks':checks})
        report={'checkedAt':datetime.now(timezone.utc).isoformat(),'url':url,'publication':expected,'checks':checks,'attempts':attempts,
                'scope':'Exact reader publication and feed health; not complete team coverage or confirmed availability'}
        (ROOT/'reviews/personnel-public-readback.json').write_text(json.dumps(report,indent=2)+'\n')
        if all(c['body'].get('publicationHash')==expected for c in checks):break
        if time.monotonic()>=deadline:raise ValueError('Site has not selected the exact personnel publication')
        time.sleep(5)
    if any(c['httpStatus']!=200 or c['body'].get('status')!='ok' for c in checks):
        raise ValueError('Publication selected but a personnel feed is unavailable')
    print(json.dumps({'publication':expected,'checks':len(checks),'status':'ok'}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='https://nfl-intelligence-one.vercel.app')
    main(parser.parse_args().url)
