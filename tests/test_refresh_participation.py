import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from refresh_participation import collect, validate


class ParticipationCollection(unittest.TestCase):
    def setUp(self):
        self.raw = gzip.decompress((Path(__file__).resolve().parents[1] / 'reviews/player-usage-2026-source.csv.gz').read_bytes())

    def test_real_source_retained_and_failure_preserves_prior(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            meta = collect(root, 2026, lambda _: self.raw)
            self.assertEqual(meta['rows'], 187)
            prior = (root / 'data/participation-source.json').read_bytes()
            self.assertEqual(gzip.decompress((root / f"data/participation-sources/{meta['sourceHash']}.csv.gz").read_bytes()), self.raw)
            for payload in (b'<html>error</html>', self.raw.splitlines()[0]+b'\n', self.raw.replace(b',2026,', b',2025,')):
                with self.assertRaises(ValueError): collect(root, 2026, lambda _: payload)
                self.assertEqual((root / 'data/participation-source.json').read_bytes(), prior)
                self.assertEqual(json.loads((root / 'data/participation-collection.json').read_text())['status'], 'failed')

    def test_duplicate_and_bad_values_fail(self):
        lines = self.raw.splitlines()
        with self.assertRaisesRegex(ValueError, 'Duplicate or blank'):
            validate(lines[0]+b',offense_pct\n'+lines[1]+b',1\n', 2026)
        with self.assertRaisesRegex(ValueError, 'Duplicate or blank'):
            validate(lines[0]+b',\n'+lines[1]+b',1\n', 2026)
        with self.assertRaises(ValueError): validate(self.raw+b'\n'+lines[1], 2026)
        import csv, io
        rows = list(csv.DictReader(io.StringIO(self.raw.decode())))
        for value in ('NaN', '-1', '1.1'):
            rows[0]['offense_pct'] = value
            output = io.StringIO(); writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader(); writer.writerows(rows)
            with self.assertRaises(ValueError): validate(output.getvalue().encode(), 2026)
