import copy
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.build_explosive_evidence import build

ROOT = Path(__file__).resolve().parents[1]


class RetainedExplosiveEvidence(unittest.TestCase):
    def test_retained_season_reproduces_artifact_and_defense_totals(self):
        manifest = json.loads((ROOT / 'data/explosive-source.json').read_text())
        result = build(manifest, ROOT)
        self.assertEqual(result, json.loads((ROOT / 'data/explosive-plays.json').read_text()))
        self.assertEqual(len(result['games']), 570)
        self.assertEqual(len(result['teams']), 32)
        for kind in ('passing', 'rushing'):
            for field in ('plays', 'explosive'):
                self.assertEqual(sum(t['offense'][kind][field] for t in result['teams'].values()),
                                 sum(t['defense'][kind][field] for t in result['teams'].values()))

    def test_modified_bytes_are_rejected_before_calculation(self):
        manifest = json.loads((ROOT / 'data/explosive-source.json').read_text())
        manifest['schedule']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            build(manifest, ROOT)

    def test_truncated_but_valid_source_cannot_hide_missing_game(self):
        manifest = json.loads((ROOT / 'data/explosive-source.json').read_text())
        with gzip.open(ROOT / manifest['plays']['path'], 'rt', newline='') as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            first = next(reader)
        text = io.StringIO()
        writer = csv.DictWriter(text, fieldnames=fields)
        writer.writeheader()
        writer.writerow(first)
        raw = gzip.compress(text.getvalue().encode(), mtime=0)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'partial.csv.gz'
            path.write_bytes(raw)
            changed = copy.deepcopy(manifest)
            changed['plays'] = {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest()}
            with self.assertRaisesRegex(ValueError, 'coverage is incomplete'):
                build(changed, ROOT)


if __name__ == '__main__': unittest.main()
