"""CI replay of a fixed real edition; isolated files and forbidden network."""
import gzip
import hashlib
import json
import re
import socket
import tempfile
import urllib.request
from pathlib import Path
from unittest.mock import patch
from replay_forecast import replay

ROOT = Path(__file__).resolve().parents[1]


def restore(source, target):
    manifest = json.loads((source / 'manifest.json').read_text())
    seen = set()
    for entry in manifest['files']:
        name = entry['path']
        if not re.fullmatch(r'data/(?:site\.json|games\.csv|raw/stats_team_week_\d{4}\.csv)', name) or name in seen:
            raise ValueError('Unsafe or duplicate fixture path')
        seen.add(name)
        sha = entry['sha256']
        if not re.fullmatch('[0-9a-f]{64}', sha) or entry['blob'] != sha + '.gz':
            raise ValueError('Invalid fixture blob identity')
        compressed = (source / entry['blob']).read_bytes()
        if hashlib.sha256(compressed).hexdigest() != entry['compressedSha256']:
            raise ValueError('Compressed fixture digest mismatch')
        raw = gzip.decompress(compressed)
        if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError('Restored fixture digest mismatch')
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    return manifest


def main():
    with tempfile.TemporaryDirectory() as folder:
        target = Path(folder)
        manifest = restore(ROOT / 'reviews/forecast-replay-inputs', target)
        before = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in target.rglob('*') if p.is_file()}
        with patch.object(urllib.request, 'urlopen', side_effect=AssertionError('Network forbidden during replay')), \
             patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden during replay')):
            report = replay(target)
        after = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in target.rglob('*') if p.is_file()}
        if before != after:
            raise ValueError('Replay modified retained evidence')
        if report['editionGeneratedAt'] != manifest['editionGeneratedAt'] or report['matched'] != manifest['expectedSnapshots'] or report['mismatches'] or report['unreplayable']:
            raise ValueError('Retained edition did not fully replay: ' + json.dumps(report))
        report['networkBlocked'] = True
        report['restoredFilesUnchanged'] = True
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
