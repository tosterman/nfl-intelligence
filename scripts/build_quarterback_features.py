"""Build candidate features for the fixed 24-hour pregame role audit."""
import csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from quarterback_form import prior_passing,form
ROOT=Path(__file__).resolve().parents[1]
HASHES={2024:'3ddc45a84f759aa348ce465ae001752c530575455717657cdfe1f8abfcdb4759',2025:'e5e0615b3d96a3eaebfaee91e55afb4a4e7fe0caf057454177bcd7d6ad4bcfc2'}
def main():
    rows=[]
    for year,digest in HASHES.items():
        path=ROOT/f'release-recovery/stats_player_week_{year}.csv'
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Unexpected player-stat bytes')
        with path.open(encoding='utf-8-sig',newline='') as source:rows.extend(csv.DictReader(source))
    schedule=ROOT/'data/games.csv'
    with schedule.open(encoding='utf-8-sig',newline='') as source:games={g['game_id']:g for g in csv.DictReader(source)}
    role_path=ROOT/'reviews/quarterback-role-evaluation.json'
    roles=json.loads(role_path.read_text())
    if hashlib.sha256(schedule.read_bytes()).hexdigest()!=roles['scheduleHash']:raise ValueError('Schedule differs from role audit')
    features=[];cache={}
    for record in roles['observations']:
        if record['hoursBeforeKickoff']!=24:continue
        cutoff=datetime.fromisoformat(record['cutoff'])
        if cutoff not in cache:cache[cutoff]=prior_passing(rows,games,cutoff)
        value=form(cache[cutoff],record['listedFirst'],cutoff) if record['listedFirst'] else {'status':'unavailable','games':0,'weightedDropbacks':0,'netYardsPerDropback':None,'sackRate':None}
        features.append({'gameId':record['gameId'],'team':record['team'],'cutoff':record['cutoff'],'listedPlayerId':record['listedFirst'],'roleStatus':'available' if record['listedFirst'] else 'unavailable','form':value})
    report={'generatedAt':datetime.now(timezone.utc).isoformat(),'statsSourceHashes':HASHES,'roleAuditHash':hashlib.sha256(role_path.read_bytes()).hexdigest(),
            'scheduleHash':roles['scheduleHash'],'halfLifeDays':90,'priorDropbacks':200,'publicationEmbargoHours':24,
            'summary':{'teamGames':len(features),'availableForm':sum(r['form']['status']=='available' for r in features),'missingRole':sum(not r['listedPlayerId'] for r in features),'roleWithoutHistory':sum(bool(r['listedPlayerId']) and r['form']['status']!='available' for r in features)},'features':features}
    (ROOT/'reviews/quarterback-feature-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['summary']))
if __name__=='__main__':main()
