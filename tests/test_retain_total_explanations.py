import hashlib
import json
from pathlib import Path
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import retain_total_explanations as retention


class TotalExplanationRetention(unittest.TestCase):
    def test_repeat_capture_is_identical_and_failed_replay_preserves_current(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(retention.ROOT / 'data/forecast-input-archive', root / 'data/forecast-input-archive')
            for name in ('site.json', 'ledger.json'):
                shutil.copy2(retention.ROOT / 'data' / name, root / 'data' / name)
            self.check_retention(root)

    def check_retention(self, root):
        retention.retain(root)
        current = root / 'data/total-explanations.json'
        before = current.read_bytes()
        watched = {p: p.read_bytes() for p in [root / 'data/site.json', root / 'data/ledger.json']}
        result = retention.retain(root)
        self.assertEqual(current.read_bytes(), before)
        self.assertEqual(hashlib.sha256(before).hexdigest(), result['artifactSha256'])
        self.assertEqual((root / f"data/total-explanation-archive/{result['artifactSha256']}.json").read_bytes(), before)
        value = json.loads(before)
        self.assertEqual(value['inputManifestSha256'], result['inputManifestSha256'])
        self.assertEqual(len(value['records']), result['records'])
        with patch.object(retention, 'build', side_effect=ValueError('unreplayable')):
            with self.assertRaises(ValueError):
                retention.retain(root)
        self.assertEqual(current.read_bytes(), before)
        self.assertTrue(all(p.read_bytes() == raw for p, raw in watched.items()))
