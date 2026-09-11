"""Prepublication verification of the exact edition's total explanations."""
import hashlib
import json
import math
from pathlib import Path
import tempfile
from build_total_explanations import ROOT, build
from forecast_input_archive import restore


def compare(saved, replay):
    for key in ('schemaVersion', 'siteSha256', 'modelCodeHash', 'explanationCodeHash', 'editionGeneratedAt', 'replayMatched'):
        if saved.get(key) != replay[key]:
            raise ValueError('Explanation provenance mismatch: ' + key)
    if saved['records'].keys() != replay['records'].keys():
        raise ValueError('Explanation coverage mismatch')
    for identity, expected in replay['records'].items():
        actual = saved['records'][identity]
        for key in expected:
            if key in ('rawTerms', 'unroundedTotal'):
                continue
            if actual.get(key) != expected[key]:
                raise ValueError('Displayed explanation differs from replay')
        if not math.isfinite(actual['unroundedTotal']) or abs(actual['unroundedTotal'] - expected['unroundedTotal']) > 1e-9:
            raise ValueError('Unrounded total differs from replay')
        if len(actual['rawTerms']) != len(expected['rawTerms']):
            raise ValueError('Raw explanation coverage mismatch')
        for left, right in zip(actual['rawTerms'], expected['rawTerms']):
            if left['name'] != right['name'] or not math.isfinite(left['points']) or abs(left['points'] - right['points']) > 1e-9:
                raise ValueError('Raw explanation differs from replay')


def verify(root=ROOT):
    raw = (root / 'data/total-explanations.json').read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if (root / f'data/total-explanation-archive/{digest}.json').read_bytes() != raw:
        raise ValueError('Explanation archive mismatch')
    saved = json.loads(raw)
    if saved['siteSha256'] != hashlib.sha256((root / 'data/site.json').read_bytes()).hexdigest():
        raise ValueError('Explanation belongs to another edition')
    with tempfile.TemporaryDirectory() as directory:
        restored = Path(directory)
        restore(root / 'data/forecast-input-archive', saved['inputManifestSha256'], restored)
        replay = build(restored)
    compare(saved, replay)
    return digest


if __name__ == '__main__':
    print('Verified total explanation artifact: ' + verify(), flush=True)
