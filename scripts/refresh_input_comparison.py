"""Bind refresh comparison to the exact edition present before acquisition."""
import argparse
import json
import re
import tempfile
from pathlib import Path
from forecast_input_archive import sha, restore
from compare_input_bundles import retain_comparison


def remember(root):
    marker = {'siteSha256': sha((root / 'data/site.json').read_bytes())}
    path = root / 'release-recovery/previous-input-edition.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(marker) + '\n')
    return marker


def find_manifest(archive, site_hash):
    for path in sorted((archive / 'manifests').glob('*.json')):
        raw = path.read_bytes()
        if not re.fullmatch('[a-f0-9]{64}', path.stem) or sha(raw) != path.stem:
            raise ValueError('Invalid archived manifest identity')
        manifest = json.loads(raw)
        if manifest.get('siteSha256') == site_hash:
            return path.stem
    return None


def finish(root):
    marker = json.loads((root / 'release-recovery/previous-input-edition.json').read_text())
    before_hash = marker.get('siteSha256')
    if not isinstance(before_hash, str) or not re.fullmatch('[a-f0-9]{64}', before_hash):
        raise ValueError('Invalid previous edition marker')
    after_hash = sha((root / 'data/site.json').read_bytes())
    archive = root / 'data/forecast-input-archive'
    before = find_manifest(archive, before_hash)
    after = find_manifest(archive, after_hash)
    if after is None:
        raise ValueError('Current edition inputs were not retained')
    if before is None:
        with tempfile.TemporaryDirectory() as directory:
            restore(archive, after, Path(directory))
        result = {'status': 'previous-inputs-unavailable', 'beforeSiteSha256': before_hash,
                  'afterSiteSha256': after_hash, 'afterManifest': after}
    else:
        result = {'status': 'compared', **retain_comparison(archive, before, after)}
    (root / 'release-recovery/input-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['remember', 'finish'])
    args = parser.parse_args()
    print(json.dumps((remember if args.action == 'remember' else finish)(Path(__file__).resolve().parents[1]), indent=2))
