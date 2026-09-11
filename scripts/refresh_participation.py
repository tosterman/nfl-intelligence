"""Retain validated participation source bytes without changing public usage."""
import csv
import gzip
import hashlib
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from forecast_input_archive import immutable
from publication import write_receipts

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {'game_id', 'season', 'week', 'game_type', 'pfr_player_id', 'team', 'opponent',
          'offense_pct', 'defense_pct', 'st_pct', 'offense_snaps', 'defense_snaps', 'st_snaps'}


def validate(raw, season):
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    if not FIELDS.issubset(reader.fieldnames or []):
        raise ValueError('Missing participation columns')
    rows, seen = [], set()
    for row in reader:
        if None in row or any(row.get(k) is None for k in FIELDS):
            raise ValueError('Malformed participation row')
        if (row['season'] != str(season) or row['game_type'] not in {'REG', 'POST'}
                or not 1 <= int(row['week']) <= 22 or not row['game_id'] or not row['pfr_player_id']
                or not row['team'] or not row['opponent'] or row['team'] == row['opponent']):
            raise ValueError('Invalid participation scope')
        identity = (row['game_id'], row['pfr_player_id'])
        if identity in seen:
            raise ValueError('Duplicate participation identity')
        seen.add(identity)
        for field in FIELDS & {'offense_pct','defense_pct','st_pct','offense_snaps','defense_snaps','st_snaps'}:
            value = float(row[field])
            if not math.isfinite(value) or value < 0 or (field.endswith('_pct') and value > 1) or (field.endswith('_snaps') and not value.is_integer()):
                raise ValueError('Invalid participation value')
        rows.append(row)
    if not rows:
        raise ValueError('Empty participation source is not zero participation')
    return rows


def collect(root, season, fetch=None):
    if isinstance(season, bool) or not isinstance(season, int) or not 1999 <= season <= 2100:
        raise ValueError('Invalid participation season')
    url = f'https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_{season}.csv'
    attempted = datetime.now(timezone.utc).isoformat()
    folder = root / 'data/participation-sources'
    folder.mkdir(parents=True, exist_ok=True)
    try:
        raw = fetch(url) if fetch else urlopen(url, timeout=45).read()
        rows = validate(raw, season)
        digest = hashlib.sha256(raw).hexdigest()
        path = folder / (digest + '.csv.gz')
        if path.exists():
            if gzip.decompress(path.read_bytes()) != raw:
                raise ValueError('Retained participation bytes conflict')
        else:
            immutable(path, gzip.compress(raw, mtime=0))
        meta = {'schemaVersion': 1, 'status': 'available', 'season': season, 'sourceUrl': url,
                'sourceHash': digest, 'retrievedAt': datetime.now(timezone.utc).isoformat(),
                'rows': len(rows), 'meaning': 'Revised observed appearances, not expected snaps or a preserved pregame vintage.'}
        write_receipts(root / 'data/participation-source.json', meta)
    except Exception as error:
        write_receipts(root / 'data/participation-collection.json', {
            'status': 'failed', 'season': season, 'attemptedAt': attempted,
            'reason': type(error).__name__,
            'previousSourceAvailable': (root / 'data/participation-source.json').exists()})
        raise
    write_receipts(root / 'data/participation-collection.json', {
        'status': 'collected', 'season': season, 'attemptedAt': attempted,
        'sourceHash': digest, 'retrievedAt': meta['retrievedAt']})
    return meta


if __name__ == '__main__':
    personnel = json.loads((ROOT / 'data/personnel.json').read_text())
    seasons = {p['season'] for p in personnel['players']}
    if len(seasons) != 1:
        raise ValueError('One personnel season required')
    print(json.dumps(collect(ROOT, seasons.pop())))
