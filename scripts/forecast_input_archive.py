"""Immutable local/Git input bundles. Retention does not establish publication."""
import argparse
import gzip
import hashlib
import json
import os
import re
from pathlib import Path
from verify_forecast_inputs import verify

ROOT = Path(__file__).resolve().parents[1]


def sha(raw): return hashlib.sha256(raw).hexdigest()


def immutable(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('xb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        pass
    if path.read_bytes() != raw:
        raise ValueError('Immutable archive object conflict or incomplete write')


def retain(root, archive):
    site_raw = (root / 'data/site.json').read_bytes()
    verified = verify(root)
    if not verified['inputsMatch']:
        raise ValueError('Cannot retain mismatched edition inputs')
    captured_site = json.loads(site_raw)
    captured_inputs = {'data/games.csv': captured_site['source']['sha256']}
    captured_inputs.update({f"data/raw/stats_team_week_{source['season']}.csv": source['sha256']
                            for source in captured_site['efficiencySources']})
    if captured_inputs != {entry['path']: entry['expectedSha256'] for entry in verified['files']} or captured_site['generatedAt'] != verified['editionGeneratedAt']:
        raise ValueError('Edition changed during input verification')
    entries = []
    # Read and validate all inputs before making a completion manifest.
    pending = [('data/site.json', site_raw, sha(site_raw))]
    pending += [(entry['path'], (root / entry['path']).read_bytes(), entry['expectedSha256'])
                for entry in verified['files']]
    if (root / 'data/site.json').read_bytes() != site_raw:
        raise ValueError('Edition changed during retention')
    for name, raw, expected in pending:
        if sha(raw) != expected:
            raise ValueError('Input changed during retention')
        object_path = archive / 'objects' / (expected + '.gz')
        try:
            immutable(object_path, gzip.compress(raw, mtime=0))
        except ValueError:
            # The key identifies decompressed bytes. Another supported compressor
            # may have already retained the same content with different encoding.
            pass
        compressed = object_path.read_bytes()
        try:
            restored = gzip.decompress(compressed)
        except (OSError, EOFError) as error:
            raise ValueError('Invalid compressed archive object') from error
        if restored != raw:
            raise ValueError('Archive object content mismatch')
        entries.append({'path': name, 'sha256': expected, 'bytes': len(raw),
                        'compressedSha256': sha(compressed)})
    manifest = {'schemaVersion': 1, 'editionGeneratedAt': verified['editionGeneratedAt'],
                'siteSha256': sha(site_raw), 'files': entries}
    raw_manifest = json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()
    identity = sha(raw_manifest)
    immutable(archive / 'manifests' / (identity + '.json'), raw_manifest)
    return {'manifestSha256': identity, 'siteSha256': sha(site_raw), 'files': len(entries)}


def restore(archive, identity, target):
    if not isinstance(identity, str) or not re.fullmatch('[a-f0-9]{64}', identity):
        raise ValueError('Invalid manifest identity')
    raw_manifest = (archive / 'manifests' / (identity + '.json')).read_bytes()
    if sha(raw_manifest) != identity:
        raise ValueError('Manifest digest mismatch')
    manifest = json.loads(raw_manifest)
    if manifest.get('schemaVersion') != 1 or not isinstance(manifest.get('files'), list):
        raise ValueError('Unsupported archive manifest')
    pending = {}; site = None
    for entry in manifest['files']:
        name, expected = entry.get('path'), entry.get('sha256')
        if not isinstance(name, str) or not re.fullmatch(r'data/(?:site\.json|games\.csv|raw/stats_team_week_\d{4}\.csv)', name) or name in pending:
            raise ValueError('Unsafe or duplicate archive path')
        if not isinstance(expected, str) or not re.fullmatch('[a-f0-9]{64}', expected):
            raise ValueError('Invalid object identity')
        compressed = (archive / 'objects' / (expected + '.gz')).read_bytes()
        if sha(compressed) != entry.get('compressedSha256'):
            raise ValueError('Compressed archive mismatch')
        raw = gzip.decompress(compressed)
        if len(raw) != entry.get('bytes') or sha(raw) != expected:
            raise ValueError('Restored input mismatch')
        pending[name] = raw
        if name == 'data/site.json': site = json.loads(raw)
    if site is None or sha(pending['data/site.json']) != manifest.get('siteSha256') or site.get('generatedAt') != manifest.get('editionGeneratedAt'):
        raise ValueError('Archive edition identity mismatch')
    required = {'data/site.json': manifest['siteSha256'], 'data/games.csv': site['source']['sha256']}
    for source in site['efficiencySources']:
        season = source['season']
        if type(season) is not int or not 1900 <= season <= 2200 or f'data/raw/stats_team_week_{season}.csv' in required:
            raise ValueError('Invalid archive season')
        required[f'data/raw/stats_team_week_{season}.csv'] = source['sha256']
    if pending.keys() != required.keys() or any(sha(pending[name]) != digest for name, digest in required.items()):
        raise ValueError('Archive does not cover edition inputs')
    for name, raw in pending.items(): immutable(target / name, raw)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ROOT / 'data/forecast-input-archive')
    args = parser.parse_args()
    print(json.dumps(retain(ROOT, args.archive), indent=2))
