"""Bind season participation to exact personnel and corroborated identity inputs."""
import csv
import gzip
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import build_data as base
from build_public_usage import indexed, FIELDS
from publication import write_receipts
from refresh_participation import validate
from season_usage import season_usage, season_phase

ROOT = Path(__file__).resolve().parents[1]


def instant(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Participation evidence requires timezone')
    return result


def build(root=ROOT, now=None):
    now = now or datetime.now(timezone.utc)
    def read(name): return json.loads((root / name).read_bytes())
    def digest(name): return hashlib.sha256((root / name).read_bytes()).hexdigest()
    personnel = read('data/personnel.json')
    identity = read('reviews/personnel-identity-audit.json')
    source = read('data/participation-source.json')
    collection = read('data/participation-collection.json')
    for name in ('personnel', 'quarterbacks'):
        if identity['inputHashes'][name] != digest(f'data/{name}.json'):
            raise ValueError('Identity audit does not match current inputs')
    if identity['codeHash'] != digest('scripts/audit_personnel_identity.py'):
        raise ValueError('Identity audit code changed')
    if source['status'] != 'available' or not re.fullmatch('[a-f0-9]{64}', source['sourceHash']):
        raise ValueError('Invalid participation source identity')
    if source['sourceUrl'] != f"https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_{source['season']}.csv":
        raise ValueError('Unsupported participation source URL')
    acquired = instant(source['retrievedAt'])
    reported = instant(personnel['retrievedAt'])
    if acquired > now or reported > now:
        raise ValueError('Future participation or personnel evidence')
    raw = gzip.decompress((root / f"data/participation-sources/{source['sourceHash']}.csv.gz").read_bytes())
    if hashlib.sha256(raw).hexdigest() != source['sourceHash']:
        raise ValueError('Participation source bytes changed')
    snaps = validate(raw, source['season'])
    registry_meta = read('reviews/player-registry-source.json')
    registry_raw = gzip.decompress((root / 'reviews/player-identity-source.csv.gz').read_bytes())
    if hashlib.sha256(registry_raw).hexdigest() != registry_meta['sha256']:
        raise ValueError('Registry source bytes changed')
    registry = list(csv.DictReader(io.StringIO(registry_raw.decode('utf-8-sig'))))
    rows = base.load_rows(root / 'data/games.csv')
    games = {r['game_id']: {'season': r['season'], 'type': season_phase(r['game_type']), 'week': r['week'],
        'kickoff': base.kickoff(r), 'teams': [r['home_team'], r['away_team']],
        'completed': r['home_score'] is not None and r['away_score'] is not None} for r in rows if r['gametime']}
    players, identities = indexed(personnel['players']), indexed(identity['records'], True)
    if players.keys() != identities.keys():
        raise ValueError('Identity audit scope differs')
    records = []
    for scope, player in players.items():
        corroboration = identities[scope]
        if corroboration['name'] != player['name'] or player['season'] != source['season']:
            raise ValueError('Player or season differs from evidence')
        weekly = [r for r in rows if (r['season'], season_phase(r['game_type']), r['week']) ==
                  (player['season'], player['type'], player['week'])]
        if not weekly or any(not r['gametime'] for r in weekly):
            raise ValueError('Incomplete weekly kickoff context')
        cutoff = min(acquired, reported, min(base.kickoff(r) for r in weekly))
        usage = season_usage(player['playerId'], registry, snaps, games, cutoff,
                             player['season'], player['type'], player['week'], player['team']) if corroboration['status'] == 'matched' else None
        records.append({field: player[field] for field in FIELDS} | {
            'identityStatus': corroboration['status'], 'cutoff': cutoff.isoformat(), 'usage': usage})
    current_capture = (collection.get('status') == 'collected' and collection.get('sourceHash') == source['sourceHash']
                       and collection.get('retrievedAt') == source['retrievedAt'] and collection.get('season') == source['season'])
    return {'schemaVersion': 1, 'calculatedAt': now.isoformat(),
            'personnelSourceHash': personnel['sourceHash'], 'personnelRetrievedAt': personnel['retrievedAt'],
            'sourceSeason': source['season'], 'sourceHash': source['sourceHash'], 'sourceRetrievedAt': source['retrievedAt'],
            'sourceUrl': source['sourceUrl'], 'collectionStatus': 'current' if current_capture else 'retained',
            'inputHashes': {'personnel': digest('data/personnel.json'), 'schedule': digest('data/games.csv'),
                # This repository-generated JSON has LF bytes in Git, including
                # when a Windows checkout supplies CRLF. Raw feed hashes remain exact.
                'identity': hashlib.sha256((root / 'reviews/personnel-identity-audit.json').read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
                'registry': registry_meta['sha256']},
            'records': records,
            'meaning': 'Earlier-week observed appearances; team partitions share the same last-eight sample. No availability, player-value or forecast adjustment.'}


if __name__ == '__main__':
    result = build()
    write_receipts(ROOT / 'data/season-participation.json', result)
    print(json.dumps({'reports': len(result['records']), 'matchedIdentities': sum(r['identityStatus'] == 'matched' for r in result['records'])}))
