"""Recompute immutable comparisons before exposing compact schedule explanations."""
import csv
import io
import json
import tempfile
from pathlib import Path
from forecast_input_archive import restore, sha
from compare_input_bundles import compare_bundles

ROOT = Path(__file__).resolve().parents[1]


def additional_pairs(archive, game_ids):
    pairs = {}
    for path in sorted((archive / 'comparisons').glob('*.json')):
        raw = path.read_bytes()
        if sha(raw) != path.stem:
            raise ValueError('Comparison identity mismatch')
        stored = json.loads(raw)
        verified = compare_bundles(archive, stored['beforeManifest'], stored['afterManifest'])
        canonical = json.dumps(verified, sort_keys=True, separators=(',', ':')).encode()
        if canonical != raw:
            raise ValueError('Comparison does not reproduce from retained inputs')
        schedule = next(file for file in verified['files'] if file['path'] == 'data/games.csv')
        with tempfile.TemporaryDirectory() as directory:
            left, right = Path(directory) / 'before', Path(directory) / 'after'
            restore(archive, stored['beforeManifest'], left)
            restore(archive, stored['afterManifest'], right)
            keys = []
            for root in (left, right):
                rows = csv.DictReader(io.StringIO((root / 'data/games.csv').read_bytes().decode('utf-8-sig')))
                keys.append({row['game_id'] for row in rows})
            compared = sorted(set(game_ids) & keys[0] & keys[1])
        pair = {'beforeSha256': schedule['beforeSha256'], 'afterSha256': schedule['afterSha256'],
                'comparedSiteGames': compared, 'changedRecords': len(schedule['revised']),
                'revisions': [{'gameId': row['key'][0], 'fields': sorted(row['fields'])} for row in schedule['revised']]}
        key = (pair['beforeSha256'], pair['afterSha256'])
        if key in pairs and pairs[key] != pair:
            raise ValueError('Conflicting evidence for the same schedule pair')
        pairs[key] = pair
    return [pairs[key] for key in sorted(pairs)]


if __name__ == '__main__':
    site = json.loads((ROOT / 'data/site.json').read_text())
    ledger = json.loads((ROOT / 'data/ledger.json').read_text())
    game_ids = {game['id'] for game in site['games']} | {snapshot['gameId'] for snapshot in ledger}
    path = ROOT / 'data/source-record-changes.json'
    primary = json.loads(path.read_text())
    primary['additionalPairs'] = [pair for pair in additional_pairs(ROOT / 'data/forecast-input-archive', game_ids)
                                 if (pair['beforeSha256'], pair['afterSha256']) != (primary['beforeSha256'], primary['afterSha256'])]
    path.write_text(json.dumps(primary, indent=2) + '\n')
    print(f"Rebuilt {len(primary['additionalPairs'])} additional verified schedule pairs")
