import sys
from pathlib import Path
import unittest
import json
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_total_explanations as builder
from forecast_input_archive import restore


class TotalExplanationReplay(unittest.TestCase):
    def test_failed_or_unreviewed_engine_cannot_produce_explanations(self):
        good = {'mismatches': 0, 'unreplayable': 0, 'matched': 15, 'modelCodeHash': builder.SUPPORTED_ENGINE}
        for changes in ({'mismatches': 1}, {'unreplayable': 1}, {'matched': 0}, {'modelCodeHash': 'new'}):
            with self.subTest(changes=changes), patch.object(builder.replay_forecast, 'replay', return_value={**good, **changes}):
                with self.assertRaises(ValueError):
                    builder.build()

    def test_actual_current_explanations_reproduce_and_preserve_snapshots(self):
        root = builder.ROOT
        watched = [root / 'data/site.json', root / 'data/ledger.json', root / 'scripts/build_data.py', root / 'scripts/experiment_model.py', root / 'scripts/refresh.py']
        before = {p: p.read_bytes() for p in watched}
        identity = json.loads((root / 'data/total-explanations.json').read_text())['inputManifestSha256']
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
