"""Read-only rehearsal of season-aware participation against retained real inputs."""
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
from datetime import datetime, timezone
import build_data as base
from season_usage import season_usage

ROOT = Path(__file__).resolve().parents[1]


def audit(root=ROOT):
    source = json.loads((root / 'reviews/player-usage-2026-feasibility.json').read_text())
    raw = gzip.decompress((root / 'reviews/player-usage-2026-source.csv.gz').read_bytes())
    if hashlib.sha256(raw).hexdigest() != source['sha256']:
        raise ValueError('Participation source hash mismatch')
    registry_raw = gzip.decompress((root / 'reviews/player-identity-source.csv.gz').read_bytes())
    registry_meta = json.loads((root / 'reviews/player-registry-source.json').read_text())
    if hashlib.sha256(registry_raw).hexdigest() != registry_meta['sha256']:
        raise ValueError('Identity registry hash mismatch')
    registry = list(csv.DictReader(io.StringIO(registry_raw.decode('utf-8-sig'))))
    snaps = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    personnel_raw = (root / 'data/personnel.json').read_bytes()
    personnel = json.loads(personnel_raw)
    schedule_raw = (root / 'data/games.csv').read_bytes()
    rows = base.load_rows(root / 'data/games.csv')
    games = {r['game_id']: {'season': r['season'], 'week': r['week'], 'type': r['game_type'],
        'kickoff': base.kickoff(r), 'teams': [r['home_team'], r['away_team']],
        'completed': r['home_score'] is not None and r['away_score'] is not None}
        for r in rows if r['gametime']}
    records = []
    for player in personnel['players']:
        scoped = [g for g in games.values() if
                  (g['season'], g['type'], g['week']) == (player['season'], player['type'], player['week'])]
        if not scoped:
            raise ValueError('Report week has no known schedule cutoff')
        cutoff = min(g['kickoff'] for g in scoped)
        evidence = season_usage(player['playerId'], registry, snaps, games, cutoff,
                                player['season'], player['type'], player['week'], player['team'])
        records.append({'playerId': player['playerId'], 'team': player['team'], 'usage': evidence})
    return {'generatedAt': datetime.now(timezone.utc).isoformat(), 'source': source,
            'inputHashes': {'registry': registry_meta['sha256'],
                'personnel': hashlib.sha256(personnel_raw).hexdigest(),
                'schedule': hashlib.sha256(schedule_raw).hexdigest()},
            'records': records,
            'scope': 'Rehearsal only. Registry join is not current-team identity corroboration; no public usage artifact or numerical forecast changes.'}


if __name__ == '__main__':
    report = audit()
    (ROOT / 'reviews/season-usage-rehearsal.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'reports': len(report['records']), 'available': sum(
        r['usage']['overall']['status'] == 'available' for r in report['records'])}))
