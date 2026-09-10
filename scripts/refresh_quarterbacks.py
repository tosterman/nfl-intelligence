"""Acquire timestamped listed QB roles; never infer confirmed starters."""
import csv,gzip,hashlib,io,json,os,tempfile,urllib.request
import re
from datetime import datetime,timezone,timedelta
from pathlib import Path
from depth_chart import quarterbacks_before,instant
ROOT=Path(__file__).resolve().parents[1]

def archive_source(raw,folder):
    """Deduplicate contiguous provider timestamps while preserving exact CSV bytes."""
    lines=raw.splitlines(keepends=True)
    if not lines or not lines[0].removeprefix(b'\xef\xbb\xbf').startswith(b'dt,'):raise ValueError('Unexpected source layout')
    chunks=folder/'raw-chunks';chunks.mkdir(parents=True,exist_ok=True)
    references=[]
    def save(block):
        digest=hashlib.sha256(block).hexdigest();path=chunks/(digest+'.gz')
        if path.exists():
            if gzip.decompress(path.read_bytes())!=block:raise ValueError('Corrupt existing source chunk')
        else:path.write_bytes(gzip.compress(block,mtime=0))
        references.append(digest)
    save(lines[0]);current=None;block=[]
    for line in lines[1:]:
        timestamp=line.partition(b',')[0]
        if not re.fullmatch(rb'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:Z|[+-]\d\d:\d\d)',timestamp):raise ValueError('Unsupported multiline or timestamp layout')
        if timestamp!=current and block:save(b''.join(block));block=[]
        block.append(line);current=timestamp
    if block:save(b''.join(block))
    digest=hashlib.sha256(raw).hexdigest()
    manifest={'sourceHash':digest,'bytes':len(raw),'chunks':references,'encoding':'Concatenate decompressed chunks in listed order to reconstruct exact source bytes'}
    (folder/(digest+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

def read(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NFLIntelligence/1.0'}),timeout=30) as response:
        raw=response.read(120_000_001)
    if len(raw)>120_000_000:raise ValueError('Depth-chart source exceeds size limit')
    return raw

def normalize(raw,teams,cutoff):
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    required={'dt','team','player_name','gsis_id','pos_grp_id','pos_slot','pos_rank','pos_abb'}
    if not required.issubset(reader.fieldnames or []):raise ValueError('Missing depth-chart columns')
    rows=[]
    for row in reader:
        if None in row or any(row.get(k) is None for k in required):raise ValueError('Malformed depth-chart row')
        rows.append(row)
    roles=quarterbacks_before(rows,teams,cutoff)
    if not any(r['status']=='available' for r in roles.values()):raise ValueError('No recent quarterback roles')
    return roles

def main():
    site=json.loads((ROOT/'data/site.json').read_text());season=site['season']
    release=json.loads(read('https://api.github.com/repos/nflverse/nflverse-data/releases/tags/depth_charts'))
    assets=[a for a in release['assets'] if a['name']==f'depth_charts_{season}.csv']
    if len(assets)!=1:raise ValueError('Expected one season depth-chart asset')
    asset=assets[0];url=f'https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_{season}.csv'
    if asset['browser_download_url']!=url:raise ValueError('Unexpected source URL')
    raw=read(url);now=datetime.now(timezone.utc);digest=hashlib.sha256(raw).hexdigest()
    if asset.get('digest')!='sha256:'+digest or asset['size']!=len(raw):raise ValueError('Source bytes disagree with release metadata')
    if not timedelta(0)<=now-instant(asset['updated_at'])<timedelta(hours=30):raise ValueError('Stale depth-chart asset')
    teams={g[side] for g in site['games'] for side in ['home','away']}
    snapshot={'season':season,'retrievedAt':now.isoformat(),'assetUpdatedAt':asset['updated_at'],'sourceUrl':url,'sourceHash':digest,
        'meaning':'Listed depth-chart role, not a confirmed game starter; provider record time is not an announcement time.',
        'teams':normalize(raw,teams,now)}
    folder=ROOT/'data/quarterback-sources';folder.mkdir(exist_ok=True)
    archive_source(raw,folder)
    encoded=(json.dumps(snapshot,sort_keys=True,separators=(',',':'))+'\n').encode()
    (folder/(hashlib.sha256(encoded).hexdigest()+'.snapshot.json.gz')).write_bytes(gzip.compress(encoded,mtime=0))
    with tempfile.NamedTemporaryFile(dir=ROOT/'data',suffix='.tmp',delete=False) as staged:
        staged.write(encoded);path=Path(staged.name)
    try:os.replace(path,ROOT/'data/quarterbacks.json')
    finally:path.unlink(missing_ok=True)
    print('Listed quarterback roles:',sum(r['status']=='available' for r in snapshot['teams'].values()),'teams. Model unchanged.')

def run_collection():
    checked=datetime.now(timezone.utc).isoformat()
    try:main();state={'status':'ok','checkedAt':checked};code=0
    except Exception as error:
        state={'status':'unavailable','checkedAt':checked,'errorType':type(error).__name__};code=1
        print('Quarterback role acquisition failed; previous snapshot retained with original timestamps.')
    (ROOT/'data/quarterback-collection.json').write_text(json.dumps(state,indent=2)+'\n')
    return code
if __name__=='__main__':raise SystemExit(run_collection())
