import sys
from pathlib import Path
import unittest
import json
import tempfile
import hashlib
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_total_explanations as builder
from forecast_input_archive import restore


class TotalExplanationReplay(unittest.TestCase):
    def test_failed_or_unreviewed_engine_cannot_produce_explanations(self):
        good = {'mismatches': 0, 'unreplayable': 0, 'matched': 15, 'modelCodeHash': builder.SUPPORTED_ENGINE, 'records': []}
        for changes in ({'mismatches': 1}, {'unreplayable': 1}, {'matched': 0}, {'modelCodeHash': 'new'}):
            with self.subTest(changes=changes), patch.object(builder.replay_forecast, 'replay', return_value={**good, **changes}):
                with self.assertRaises(ValueError):
                    builder.build()

    def test_no_new_forecasts_produces_explicit_empty_explanations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            raw = json.dumps({'generatedAt': '2026-09-15T00:00:00Z', 'efficiencySources': [], 'games': []}).encode()
            (root / 'data/site.json').write_bytes(raw)
            replay = {'mismatches': 0, 'unreplayable': 0, 'matched': 0,
                      'modelCodeHash': builder.SUPPORTED_ENGINE, 'records': [],
                      'siteSha256': hashlib.sha256(raw).hexdigest()}
            with patch.object(builder.replay_forecast, 'replay', return_value=replay), \
                 patch.object(builder.refresh.base, 'load_rows', return_value=[]), \
                 patch.object(builder.replay_forecast, 'verify', return_value={'inputsMatch': True}):
                report = builder.build(root)
            self.assertEqual(report['records'], {})
            self.assertEqual(report['replayMatched'], 0)

    def test_actual_current_explanations_reproduce_and_preserve_snapshots(self):
        root = builder.ROOT
        watched = [root / 'data/site.json', root / 'data/ledger.json', root / 'scripts/build_data.py', root / 'scripts/experiment_model.py', root / 'scripts/refresh.py']
        before = {p: p.read_bytes() for p in watched}
        identity = json.loads((root / 'data/total-explanation-archive/187b903b528dc2e39bc1ce5b92c4a3ec3d545bcf778f8f8bc3278f4c621519c0.json').read_text())['inputManifestSha256']
        with tempfile.TemporaryDirectory() as directory:
            restored = Path(directory)
            restore(root / 'data/forecast-input-archive', identity, restored)
            report = builder.build(restored)
        self.assertEqual(len(report['records']), report['replayMatched'])
        self.assertGreater(report['replayMatched'], 0)
        for identity, row in report['records'].items():
            self.assertEqual(identity, row['snapshotHash'])
            self.assertAlmostEqual(sum(t['points'] for t in row['terms']), row['total'], places=8)
        self.assertTrue(all(p.read_bytes() == raw for p, raw in before.items()))
