"""Inspect current injury coverage without publishing player claims or model features."""
import csv, hashlib, io, json, urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'NFLIntelligence-source-audit'})
    with urllib.request.urlopen(request, timeout=25) as response:
        raw = response.read(10_000_001)
    if len(raw) > 10_000_000:
        raise ValueError('Source exceeds audit limit')
    return raw

def main():
    site = json.loads((ROOT / 'data/site.json').read_text())
    season = site['season']
    release = json.loads(read('https://api.github.com/repos/nflverse/nflverse-data/releases/tags/injuries'))
    matches = [a for a in release['assets'] if a['name'] == f'injuries_{season}.csv']
    if len(matches) != 1:
        raise ValueError('Expected one current-season CSV')
    asset = matches[0]
    url = f'https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_{season}.csv'
    if asset['browser_download_url'] != url:
        raise ValueError('Unexpected asset URL')
    raw = read(url)
    digest = hashlib.sha256(raw).hexdigest()
    if asset.get('digest') != 'sha256:' + digest or asset['size'] != len(raw):
        raise ValueError('Release identity changed or bytes failed verification; rerun audit')
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    rows = list(reader)
    required = {'season', 'team', 'week', 'gsis_id', 'report_status', 'practice_status'}
    if not required.issubset(reader.fieldnames or []) or not rows:
        raise ValueError('Injury schema missing required fields or rows')
    if any(r['season'] != str(season) for r in rows):
        raise ValueError('Unexpected season')
    teams = {g[side] for g in site['games'] for side in ('home', 'away')}
    present = {r['team'] for r in rows}
    keys = Counter((r['season'], r.get('game_type'), r['week'], r['team'], r['gsis_id']) for r in rows)
    report = {
        'retrievedAt': datetime.now(timezone.utc).isoformat(), 'sourceUrl': url,
        'assetUpdatedAt': asset['updated_at'], 'sha256': digest, 'bytes': len(raw),
        'season': season, 'rows': len(rows), 'columns': reader.fieldnames,
        'weeks': sorted({r['week'] for r in rows}), 'teamsPresent': sorted(present),
        'teamsWithoutRows': sorted(teams - present), 'unexpectedTeams': sorted(present - teams),
        'duplicatePlayerWeekKeys': sum(n - 1 for n in keys.values() if n > 1),
        'missingPlayerIds': sum(not r['gsis_id'] for r in rows),
        'reportStatusCounts': dict(Counter(r['report_status'] or 'UNREPORTED' for r in rows)),
        'practiceStatusCounts': dict(Counter(r['practice_status'] or 'UNREPORTED' for r in rows)),
        'hasPerReportTimestamp': 'date_modified' in (reader.fieldnames or []),
        'interpretation': 'File acquisition and asset update times do not establish individual report times. Missing team rows do not mean healthy. No numerical model adjustment.',
    }
    folder = ROOT / 'release-recovery/personnel'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / (digest + '.csv')).write_bytes(raw)
    (folder / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
