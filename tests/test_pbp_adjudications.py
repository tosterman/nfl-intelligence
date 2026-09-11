import hashlib
import json
import unittest
import csv
import gzip
import io
from pathlib import Path
from scripts.pbp_adjudications import apply_adjudications


class Adjudications(unittest.TestCase):
    def test_retained_record_matches_adjudication_without_newline_translation(self):
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / 'data/explosive-source.json').read_text())
        decisions = json.loads((root / 'data/red-zone-adjudications.json').read_text())
        raw = (root / manifest['plays']['path']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), decisions['sourceSha256'])
        rows = list(csv.DictReader(io.StringIO(gzip.decompress(raw).decode())))
        output = apply_adjudications(rows, decisions['sourceSha256'], decisions)
        self.assertEqual(len(rows) - len(output), 1)
        self.assertFalse(any(r['game_id'] == '2025_03_CIN_MIN' and r['play_id'] == '3284' for r in output))

    def setUp(self):
        self.row = {'game_id': '2025_03_CIN_MIN', 'play_id': '3284', 'play_type': 'kickoff'}
        self.decision = {'sourceSha256': 'a' * 64, 'decisions': [{'gameId': self.row['game_id'],
            'playId': self.row['play_id'], 'action': 'exclude-nullified-kickoff',
            'rowSha256': hashlib.sha256(json.dumps(self.row, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}]}

    def test_exact_adjudicated_row_is_excluded_without_mutation(self):
        following = {**self.row, 'play_id': '3300'}
        rows = [self.row, following]
        self.assertEqual(apply_adjudications(rows, 'a' * 64, self.decision), [following])
        self.assertEqual(len(rows), 2)

    def test_changed_source_row_or_missing_record_cannot_reuse_decision(self):
        for rows, digest in [([self.row], 'b' * 64), ([{**self.row, 'new_field': 'x'}], 'a' * 64), ([], 'a' * 64), ([self.row, self.row], 'a' * 64)]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                apply_adjudications(rows, digest, self.decision)


if __name__ == '__main__': unittest.main()
