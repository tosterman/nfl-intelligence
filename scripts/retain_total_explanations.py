"""Build total explanations from a restored exact input bundle, then retain them."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
from build_total_explanations import ROOT, build
from forecast_input_archive import restore, immutable
from retained_total_records import collect


def retain(root=ROOT):
    edition = hashlib.sha256((root / 'data/site.json').read_bytes()).hexdigest()
    archive = root / 'data/forecast-input-archive'
    matching = []
    for path in sorted((archive / 'manifests').glob('*.json')):
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != path.stem:
            raise ValueError('Input manifest identity mismatch')
        if json.loads(raw).get('siteSha256') == edition:
            matching.append(path.stem)
    if not matching:
        raise ValueError('No retained input bundle for current edition')
    identity = matching[0]
    with tempfile.TemporaryDirectory() as directory:
        restored = Path(directory)
        restore(archive, identity, restored)
        report = build(restored)
    if report['siteSha256'] != edition or hashlib.sha256((root / 'data/site.json').read_bytes()).hexdigest() != edition:
        raise ValueError('Edition changed during explanation retention')
    report['inputManifestSha256'] = identity
    report['retainedRecords'] = collect(root, report)
    report['retentionCodeHash'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    raw = (json.dumps(report, sort_keys=True, separators=(',', ':')) + '\n').encode()
    digest = hashlib.sha256(raw).hexdigest()
    immutable(root / f'data/total-explanation-archive/{digest}.json', raw)
    with tempfile.NamedTemporaryFile(dir=root / 'data', delete=False) as stream:
        stream.write(raw)
        temporary = stream.name
    try:
        os.replace(temporary, root / 'data/total-explanations.json')
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {'artifactSha256': digest, 'inputManifestSha256': identity, 'records': len(report['records'])}


if __name__ == '__main__':
    print(json.dumps(retain()), flush=True)
