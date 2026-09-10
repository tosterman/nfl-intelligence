"""Collect attributed practice/report snapshots; never modifies model forecasts."""
import csv, gzip, hashlib, io, json, re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from audit_personnel import read

ROOT = Path(__file__).resolve().parents[1]
REPORTS = {'Out', 'Doubtful', 'Questionable'}
PRACTICES = {'Did Not Participate In Practice', 'Limited Participation in Practice', 'Full Participation in Practice'}

def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timezone required')
    return parsed

def normalize(raw, season, teams):
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    required = {'season', 'game_type', 'team', 'week', 'gsis_id', 'full_name', 'position', 'report_status', 'practice_status'}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError('Missing personnel columns')
    result, keys = [], set()
    for row in reader:
        if None in row or any(row.get(k) is None for k in required):
            raise ValueError('Malformed personnel row')
        week = int(row['week'])
        if row['season'] != str(season) or row['team'] not in teams or row['game_type'] not in {'REG', 'POST'} or not 1 <= week <= 22:
            raise ValueError('Invalid personnel scope')
        if row.get('season_type', row['game_type']) != row['game_type']:
            raise ValueError('Conflicting season types')
        if not re.fullmatch(r'\d{2}-\d{7}', row['gsis_id']) or not row['full_name'].strip() or not row['position'].strip():
            raise ValueError('Missing player identity')
        key = (row['game_type'], week, row['team'], row['gsis_id'])
        if key in keys:
            raise ValueError('Duplicate player/week identity')
        keys.add(key)
        report, practice = row['report_status'], row['practice_status']
        if report and report not in REPORTS or practice and practice not in PRACTICES:
            raise ValueError('Unknown status vocabulary')
        result.append({'season': season, 'type': row['game_type'], 'week': week, 'team': row['team'],
                       'playerId': row['gsis_id'], 'name': row['full_name'], 'position': row['position'],
                       'reportStatus': report or None, 'practiceStatus': practice or None,
                       'reportInjury': row.get('report_primary_injury') or None,
                       'practiceInjury': row.get('practice_primary_injury') or None,
                       'practiceSecondaryInjury': row.get('practice_secondary_injury') or None,
                       'reportUpdatedAt': None})
    if not result:
        raise ValueError('Empty source does not prove healthy rosters')
    return result

def for_game(snapshot, game, now):
    """Only expose recently acquired pregame observations for an exact scope."""
    unknown = {'status': 'unavailable', 'players': []}
    if snapshot.get('status') != 'available' or not game.get('kickoff') or game.get('status') == 'final':
        return unknown
    acquired = timestamp(snapshot['retrievedAt'])
    updated = timestamp(snapshot['assetUpdatedAt'])
    kickoff = timestamp(game['kickoff'])
    if acquired >= kickoff or now >= kickoff:
        return unknown | {'reason': 'Pregame collection closed'}
    if not timedelta(0) <= now - acquired <= timedelta(hours=30) or not timedelta(0) <= now - updated <= timedelta(hours=30):
        return unknown | {'reason': 'Snapshot stale or future-dated'}
    game_type = 'POST' if game['type'] in {'WC', 'DIV', 'CON', 'SB'} else game['type']
    players = [r for r in snapshot['players'] if r['season'] == game['season'] and r['type'] == game_type and r['week'] == game['week'] and r['team'] in (game['home'], game['away'])]
    return {'status': 'snapshot', 'players': players,
            'teamsWithoutRows': [t for t in (game['away'], game['home']) if not any(r['team'] == t for r in players)]}

def main():
    site = json.loads((ROOT / 'data/site.json').read_text())
    season = site['season']
    release = json.loads(read('https://api.github.com/repos/nflverse/nflverse-data/releases/tags/injuries'))
    assets = [a for a in release['assets'] if a['name'] == f'injuries_{season}.csv']
    if len(assets) != 1:
        raise ValueError('Expected one injury source')
    asset = assets[0]
    url = f'https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_{season}.csv'
    if asset['browser_download_url'] != url:
        raise ValueError('Unexpected source URL')
    raw = read(url)
    retrieved = datetime.now(timezone.utc)
    digest = hashlib.sha256(raw).hexdigest()
    if asset.get('digest') != 'sha256:' + digest or asset['size'] != len(raw):
        raise ValueError('Source bytes disagree with release metadata')
    if not timedelta(0) <= retrieved - timestamp(asset['updated_at']) <= timedelta(hours=30):
        raise ValueError('Source asset stale or future-dated')
    teams = {g[side] for g in site['games'] for side in ('home', 'away')}
    players = normalize(raw, season, teams)
    snapshot = {'schemaVersion': 1, 'status': 'available', 'season': season, 'retrievedAt': retrieved.isoformat(),
                'assetUpdatedAt': asset['updated_at'], 'sourceUrl': url, 'sourceHash': digest,
                'attribution': 'nflverse injury and practice reports',
                'licenseUrl': 'https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md',
                'transformation': 'Normalized names and empty statuses; report times unavailable. No numerical model adjustment.',
                'players': players}
    folder = ROOT / 'data/personnel-sources'
    folder.mkdir(exist_ok=True)
    (folder / (digest + '.csv.gz')).write_bytes(gzip.compress(raw, mtime=0))
    encoded = (json.dumps(snapshot, sort_keys=True, separators=(',', ':')) + '\n').encode()
    capture_hash = hashlib.sha256(encoded).hexdigest()
    (folder / (capture_hash + '.snapshot.json.gz')).write_bytes(gzip.compress(encoded, mtime=0))
    (ROOT / 'data/personnel.json').write_bytes(encoded)
    print(f'Personnel snapshot: {len(players)} rows; source {digest}. Model unchanged.')

if __name__ == '__main__':
    main()
