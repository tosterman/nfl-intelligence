"""Recover selected historical explanations from native, replayed archive records."""
import hashlib
import json
from pathlib import Path
import tempfile
from build_total_explanations import build
from forecast_input_archive import restore


def collect(root, current):
    from verify_total_explanations import compare
    site = json.loads((root / 'data/site.json').read_bytes())
    selected = {g['snapshot']['hash']: g['snapshot'] for g in site['games'] if g.get('snapshot')}
    needed = selected.keys() - current['records'].keys()
    retained = {}
    for path in sorted((root / 'data/total-explanation-archive').glob('*.json')):
        raw = path.read_bytes()
        origin = json.loads(raw)
        candidates = needed & origin.get('records', {}).keys()
        if not candidates or origin.get('explanationCodeHash') != current['explanationCodeHash']:
            continue
        if hashlib.sha256(raw).hexdigest() != path.stem:
            raise ValueError('Retained explanation archive identity mismatch')
        with tempfile.TemporaryDirectory() as directory:
            restored = Path(directory)
            restore(root / 'data/forecast-input-archive', origin['inputManifestSha256'], restored)
            compare(origin, build(restored))
        for identity in sorted(candidates):
            snapshot = selected[identity]
            row = origin['records'][identity]
            if (origin['modelCodeHash'] != snapshot['modelCodeHash'] or row['snapshotHash'] != identity
                    or row['gameId'] != snapshot['gameId'] or row['total'] != snapshot['prediction']['total']):
                raise ValueError('Retained explanation snapshot mismatch')
            entry = {key: origin[key] for key in ('schemaVersion', 'modelCodeHash', 'explanationCodeHash', 'inputManifestSha256')}
            entry.update(artifactSha256=path.stem, record=row)
            if identity in retained:
                previous = retained[identity]
                if previous['modelCodeHash'] != entry['modelCodeHash']:
                    raise ValueError('Conflicting retained explanations')
                compare({**origin, 'records': {identity: previous['record']}},
                        {**origin, 'records': {identity: row}})
                continue
            retained[identity] = entry
    return retained
