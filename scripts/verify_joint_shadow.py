"""Fetch exact immutable GitHub bytes before granting shadow publication evidence."""
import gzip,hashlib,json,re,sys
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[1]

def verify_capture(manifest,compressed,observed,http_date):
    if len(compressed)!=manifest['compressedBytes'] or hashlib.sha256(compressed).hexdigest()!=manifest['compressedHash']:raise ValueError('Published compressed bytes differ')
    raw=gzip.decompress(compressed)
    if hashlib.sha256(raw).hexdigest()!=manifest['sha256']:raise ValueError('Published payload differs')
    data=json.loads(raw);generated=datetime.fromisoformat(data['generatedAt'])
    if data['generatedAt']!=manifest['generatedAt'] or len(data['records'])!=manifest['games'] or len({r['gameId'] for r in data['records']})!=len(data['records']):raise ValueError('Manifest scope differs')
    if not generated<=http_date<=observed or generated>observed:raise ValueError('Publication timestamps out of order')
    if any(observed>=datetime.fromisoformat(r['kickoff']) for r in data['records']):raise ValueError('Publication verification not before every kickoff')
    return data

def main(commit,digest):
    if not re.fullmatch('[a-f0-9]{40}',commit) or not re.fullmatch('[a-f0-9]{64}',digest):raise ValueError('Require exact commit and archive hash')
    folder=ROOT/'reviews/joint-shadow';manifest=json.loads((folder/(digest+'.manifest.json')).read_text())
    expected='reviews/joint-shadow/'+digest+'.json.gz'
    if manifest['archive']!=expected or manifest['sha256']!=digest:raise ValueError('Unexpected archive identity')
    url='https://raw.githubusercontent.com/tosterman/nfl-intelligence/'+commit+'/'+expected
    with urlopen(url,timeout=30) as response:
        if response.status!=200:raise ValueError('Archive unavailable')
        compressed=response.read(10000001);http_date=parsedate_to_datetime(response.headers['Date'])
    observed=datetime.now(timezone.utc);data=verify_capture(manifest,compressed,observed,http_date)
    receipt={'status':'verified-before-kickoff','observedAt':observed.isoformat(),'githubHttpDate':http_date.isoformat(),'commit':commit,'url':url,'archive':expected,'sha256':digest,'compressedHash':manifest['compressedHash'],'generatedAt':data['generatedAt'],'gameIds':[r['gameId'] for r in data['records']],'verifierHash':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with (folder/(digest+'.publication.json')).open('x') as output:output.write(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main(*sys.argv[1:])
