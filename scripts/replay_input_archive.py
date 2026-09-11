"""Replay a specified retained input bundle with network access forbidden."""
import argparse
import json
import socket
import tempfile
import urllib.request
from pathlib import Path
from unittest.mock import patch
from forecast_input_archive import restore
from replay_forecast import replay

ROOT = Path(__file__).resolve().parents[1]


def verify_archive(identity, archive):
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory)
        manifest = restore(archive, identity, target)
        with patch.object(urllib.request, 'urlopen', side_effect=AssertionError('Network forbidden')), \
             patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden')):
            report = replay(target)
        if report['mismatches'] or report['unreplayable'] or not report['matched']:
            raise ValueError('Retained bundle did not fully replay')
    return {'manifestSha256': identity, 'siteSha256': manifest['siteSha256'],
            'networkBlocked': True, **report}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest_sha256')
    parser.add_argument('--archive', type=Path, default=ROOT / 'data/forecast-input-archive')
    args = parser.parse_args()
    report = verify_archive(args.manifest_sha256, args.archive)
    (ROOT / 'reviews/input-archive-replay.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'records'}, indent=2))
