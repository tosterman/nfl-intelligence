"""Build historical inside-20 possession evidence from verified retained inputs."""
import collections
import csv
from datetime import date
import gzip
import hashlib
import io
import json
from pathlib import Path

try:
    from .red_zone_possessions import drive_evidence
    from .pbp_adjudications import apply_adjudications
except ImportError:
    from red_zone_possessions import drive_evidence
    from pbp_adjudications import apply_adjudications


def summarize_drives(plays, schedule, cutoff, season):
    boundary = date.fromisoformat(cutoff)
    known = {}
    for game in schedule:
        if game['game_id'] in known:
            raise ValueError('Duplicate schedule identity')
        known[game['game_id']] = game
    eligible = {key: g for key, g in known.items()
                if key.startswith(str(season) + '_') and date.fromisoformat(g['gameday']) < boundary
                and all(g.get(k) not in ('', None, 'NA') for k in ('home_score', 'away_score'))}
    groups, seen = collections.defaultdict(list), set()
    for row in plays:
        game_id = row['game_id']
        if game_id not in known:
            raise ValueError('Play absent from schedule')
        if game_id not in eligible:
            continue
        if row['game_date'] != eligible[game_id]['gameday']:
            raise ValueError('Play date differs from schedule')
        identity = (game_id, row['play_id'])
        if identity in seen or not row['fixed_drive']:
            raise ValueError('Duplicate play or missing drive')
        seen.add(identity)
        groups[(game_id, row['fixed_drive'])].append(row)
    results = []
    for (game_id, drive_id), rows in groups.items():
        evidence = drive_evidence(rows)
        if evidence is None:
            continue
        game = eligible[game_id]
        if {evidence['offense'], evidence['defense']} != {game['home_team'], game['away_team']}:
            raise ValueError('Possession participants differ from schedule')
        results.append({'gameId': game_id, 'driveId': drive_id, 'date': game['gameday'], **evidence})
    expected = {(key, team) for key, g in eligible.items() for team in (g['home_team'], g['away_team'])}
    if {(r['gameId'], r['offense']) for r in results} != expected:
        raise ValueError('Completed-game offense coverage incomplete')
    return results


def build(root):
    manifest = json.loads((root / 'data/explosive-source.json').read_text())
    adjudications = json.loads((root / 'data/red-zone-adjudications.json').read_text())

    def read(key):
        source = manifest[key]
        raw = (root / source['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != source['sha256']:
            raise ValueError(f'{key} source digest mismatch')
        return list(csv.DictReader(io.StringIO(gzip.decompress(raw).decode('utf-8-sig'))))

    plays = apply_adjudications(read('plays'), manifest['plays']['sha256'], adjudications)
    drives = summarize_drives(plays, read('schedule'), manifest['cutoff'], manifest['season'])
    if not drives:
        raise ValueError('No eligible possession evidence')
    teams = {}
    for drive in drives:
        for side, team in [('offense', drive['offense']), ('defense', drive['defense'])]:
            entry = teams.setdefault(team, {'offense': {'possessions': 0, 'touchdowns': 0},
                                           'defense': {'possessions': 0, 'touchdowns': 0}})[side]
            if drive['inside20']:
                entry['possessions'] += 1
                entry['touchdowns'] += int(drive['offensiveTouchdown'])
    return {'schemaVersion': 1, 'season': manifest['season'], 'cutoff': manifest['cutoff'],
            'definition': 'At least one pre-snap position strictly inside the opponent 20; each possession counted once; offensive touchdowns only',
            'includesPostseason': True, 'sourceSha256': manifest['plays']['sha256'],
            'scheduleSha256': manifest['schedule']['sha256'],
            'adjudicationHash': hashlib.sha256(json.dumps(adjudications, sort_keys=True).encode()).hexdigest(),
            'teams': dict(sorted(teams.items())), 'drives': drives}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    artifact = build(root)
    (root / 'data/red-zone.json').write_text(json.dumps(artifact, indent=2) + '\n')
    print(f"Verified {len(artifact['drives'])} possessions across {len(artifact['teams'])} teams")
