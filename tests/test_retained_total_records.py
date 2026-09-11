import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import retained_total_records as retention


class RetainedTotals(unittest.TestCase):
    def test_duplicate_origins_allow_only_raw_replay_tolerance(self):
        fixture = Path(__file__).resolve().parents[1] / 'data/total-explanation-archive/187b903b528dc2e39bc1ce5b92c4a3ec3d545bcf778f8f8bc3278f4c621519c0.json'
        origin = json.loads(fixture.read_text())
        identity, row = next(iter(origin['records'].items()))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / 'data/total-explanation-archive'
            archive.mkdir(parents=True)
            (root / 'data/site.json').write_text(json.dumps({'games': [{'snapshot': {
                'hash': identity, 'gameId': row['gameId'], 'modelCodeHash': origin['modelCodeHash'],
                'prediction': {'total': row['total']}}}]}))
            def save(value):
                raw = json.dumps(value).encode()
                path = archive / (hashlib.sha256(raw).hexdigest() + '.json')
                path.write_bytes(raw)
                return path
            save(origin)
            varied = copy.deepcopy(origin)
            varied['records'][identity]['rawTerms'][0]['points'] += 1e-11
            varied['records'][identity]['unroundedTotal'] += 1e-11
            second = save(varied)
            current = {**origin, 'records': {}}
            with patch.object(retention, 'restore'), patch.object(retention, 'build', return_value=origin):
                self.assertIn(identity, retention.collect(root, current))
                second.unlink()
                varied['records'][identity]['terms'][0]['points'] += .001
                save(varied)
                with self.assertRaisesRegex(ValueError, 'Displayed explanation'):
                    retention.collect(root, current)

    def test_native_origins_only_and_snapshot_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / 'data/total-explanation-archive'
            archive.mkdir(parents=True)
            row = {'snapshotHash': 's', 'gameId': 'game', 'total': 42}
            origin = {'schemaVersion': 1, 'modelCodeHash': 'engine', 'explanationCodeHash': 'code',
                      'inputManifestSha256': 'manifest', 'records': {'s': row}}
            raw = json.dumps(origin).encode()
            path = archive / (hashlib.sha256(raw).hexdigest() + '.json')
            path.write_bytes(raw)
            snapshot = {'hash': 's', 'gameId': 'game', 'modelCodeHash': 'engine', 'prediction': {'total': 42}}
            site = root / 'data/site.json'
            site.write_text(json.dumps({'games': [{'snapshot': snapshot}]}))
            current = {'records': {}, 'explanationCodeHash': 'code'}
            with patch.object(retention, 'restore'), patch.object(retention, 'build', return_value=origin), patch('verify_total_explanations.compare'):
                result = retention.collect(root, current)
                self.assertEqual(result['s']['record'], row)
                self.assertEqual(result['s']['artifactSha256'], path.stem)
                self.assertEqual(retention.collect(root, {**current, 'records': {'s': row}}), {})
                snapshot['prediction']['total'] = 43
                site.write_text(json.dumps({'games': [{'snapshot': snapshot}]}))
                with self.assertRaisesRegex(ValueError, 'snapshot mismatch'):
                    retention.collect(root, current)
                site.write_text(json.dumps({'games': [{'snapshot': {**snapshot, 'prediction': {'total': 42}}}]}))
                path.write_bytes(raw + b' ')
                with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                    retention.collect(root, current)
                path.unlink()
                recursive = {**origin, 'records': {}, 'retainedRecords': result}
                raw = json.dumps(recursive).encode()
                (archive / (hashlib.sha256(raw).hexdigest() + '.json')).write_bytes(raw)
                self.assertEqual(retention.collect(root, current), {})

    def test_real_zero_new_refresh_replays_original_bundle(self):
        root = Path(__file__).resolve().parents[1]
        current = json.loads((root / 'data/total-explanations.json').read_text())
        result = retention.collect(root, {**current, 'records': {}})
        self.assertGreater(len(result), 0)
        selected = {g['snapshot']['hash'] for g in json.loads((root / 'data/site.json').read_text())['games'] if g.get('snapshot')}
        self.assertTrue(set(result) <= selected)
