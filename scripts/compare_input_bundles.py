"""Compare exact retained editions; file differences do not establish model causality."""
import argparse
import json
import tempfile
from datetime import datetime
from pathlib import Path
from forecast_input_archive import restore, immutable, sha
from source_record_changes import compare_csv


def compare_bundles(archive, before, after):
    with tempfile.TemporaryDirectory() as folder:
        left, right = Path(folder) / 'before', Path(folder) / 'after'
        old = restore(archive, before, left)
        new = restore(archive, after, right)
        timestamps = [datetime.fromisoformat(value['editionGeneratedAt'].replace('Z', '+00:00')) for value in (old, new)]
        if any(value.tzinfo is None for value in timestamps) or timestamps[1] < timestamps[0]:
            raise ValueError('Bundle chronology is missing or reversed')
        old_files = {entry['path']: entry for entry in old['files'] if entry['path'] != 'data/site.json'}
        new_files = {entry['path']: entry for entry in new['files'] if entry['path'] != 'data/site.json'}
        compared = []
        for name in sorted(old_files.keys() & new_files.keys()):
            result = compare_csv((left / name).read_bytes(), (right / name).read_bytes(),
                                 old_files[name]['sha256'], new_files[name]['sha256'],
                                 ('game_id',) if name == 'data/games.csv' else ('game_id', 'team'))
            compared.append({'path': name, **result})
    return {'schemaVersion': 1, 'beforeManifest': before, 'afterManifest': after,
            'beforeEdition': old['editionGeneratedAt'], 'afterEdition': new['editionGeneratedAt'],
            'beforeSiteSha256': old['siteSha256'], 'afterSiteSha256': new['siteSha256'],
            'addedSources': [new_files[name] for name in sorted(new_files.keys() - old_files.keys())],
            'removedSources': [old_files[name] for name in sorted(old_files.keys() - new_files.keys())],
            'files': compared,
            'scope': 'Exact retained input differences. Edition generation order is not original source availability or proof of forecast causality.'}


def retain_comparison(archive, before, after):
    result = compare_bundles(archive, before, after)
    raw = json.dumps(result, sort_keys=True, separators=(',', ':')).encode()
    identity = sha(raw)
    immutable(archive / 'comparisons' / (identity + '.json'), raw)
    return {'comparisonSha256': identity, 'beforeManifest': before, 'afterManifest': after,
            'comparedFiles': len(result['files'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before_manifest')
    parser.add_argument('after_manifest')
    parser.add_argument('--archive', type=Path, default=Path(__file__).resolve().parents[1] / 'data/forecast-input-archive')
    args = parser.parse_args()
    print(json.dumps(retain_comparison(args.archive, args.before_manifest, args.after_manifest), indent=2))
