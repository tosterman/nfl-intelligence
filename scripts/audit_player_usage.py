"""Audit 2025 usage for current reported players; never adjusts forecasts."""
import csv,gzip,hashlib,io,json
from datetime import datetime,timezone
from pathlib import Path
import build_data as base
from player_usage import prior_usage
ROOT=Path(__file__).resolve().parents[1]
SNAP_HASH='80b02a6e511aa20283551cae622b29ba4d0a6f006c489a2d91591fcad33792e7'

def main():
    raw=gzip.decompress((ROOT/'reviews/player-usage-source.csv.gz').read_bytes())
    if hashlib.sha256(raw).hexdigest()!=SNAP_HASH:raise ValueError('Snap source mismatch')
    registry_raw=gzip.decompress((ROOT/'reviews/player-identity-source.csv.gz').read_bytes())
    registry_source=json.loads((ROOT/'reviews/player-registry-source.json').read_text())
    if hashlib.sha256(registry_raw).hexdigest()!=registry_source['sha256']:raise ValueError('Registry source mismatch')
    registry=list(csv.DictReader(io.StringIO(registry_raw.decode('utf-8-sig'))));snaps=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    if any(r['season']!='2025' for r in snaps):raise ValueError('Expected 2025 source only')
    schedule=ROOT/'data/games.csv';rows=base.load_rows(schedule)
    games={r['game_id']:{'kickoff':base.kickoff(r),'teams':[r['home_team'],r['away_team']],'completed':r['home_score'] is not None and r['away_score'] is not None} for r in rows if r['gametime']}
    source_path=ROOT/'data/personnel.json';personnel=json.loads(source_path.read_text());now=datetime.now(timezone.utc)
    records=[{k:p[k] for k in ['playerId','name','team','season','type','week','reportStatus']} | {'usage':prior_usage(p['playerId'],registry,snaps,games,now)} for p in personnel['players']]
    report={'generatedAt':now.isoformat(),'sourceSeason':2025,'snapSourceUrl':'https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_2025.csv',
        'snapSourceHash':SNAP_HASH,'registrySourceHash':registry_source['sha256'],'scheduleHash':hashlib.sha256(schedule.read_bytes()).hexdigest(),
        'personnelArtifactHash':hashlib.sha256(source_path.read_bytes()).hexdigest(),
        'codeHashes':{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in ['player_usage.py','audit_player_usage.py','build_data.py']},
        'available':sum(r['usage']['status']=='available' for r in records),'unavailable':sum(r['usage']['status']!='available' for r in records),
        'meaning':'2025 historical appearances only, not a current snap projection or point adjustment. Current revised data, not vintage backtest inputs.',
        'records':records}
    (ROOT/'reviews/player-usage-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
    print(json.dumps([{'name':r['name'],'status':r['reportStatus'],'usage':{k:v for k,v in r['usage'].items() if k!='games'}} for r in records if r['reportStatus']=='Out'],indent=2))

if __name__=='__main__':main()
