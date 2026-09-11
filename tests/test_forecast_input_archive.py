import hashlib
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from forecast_input_archive import retain, restore


class ForecastInputArchiveTests(unittest.TestCase):
    def fixture(self, root):
        (root / 'data/raw').mkdir(parents=True)
        schedule, stats = b'game_id\na\n', b'game_id,team\na,DET\n'
        (root / 'data/games.csv').write_bytes(schedule)
        (root / 'data/raw/stats_team_week_2025.csv').write_bytes(stats)
        site = {'generatedAt': '2026-09-11T10:00:00Z', 'source': {'sha256': hashlib.sha256(schedule).hexdigest()},
                'efficiencySources': [{'season': 2025, 'sha256': hashlib.sha256(stats).hexdigest()}]}
        (root / 'data/site.json').write_text(json.dumps(site))

    def test_roundtrip_and_identical_retention_reuse_verified_objects(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.fixture(root)
            archive = root / 'archive'
            receipt = retain(root, archive)
            self.assertEqual(receipt, retain(root, archive))
            restored = root / 'restored'
            restore(archive, receipt['manifestSha256'], restored)
            for path in (root / 'data').rglob('*'):
                if path.is_file(): self.assertEqual(path.read_bytes(), (restored / path.relative_to(root)).read_bytes())
            self.assertEqual(len(list((archive / 'objects').glob('*.gz'))), 3)

    def test_source_mismatch_writes_no_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.fixture(root)
            (root / 'data/games.csv').write_bytes(b'changed')
            with self.assertRaises(ValueError): retain(root, root / 'archive')
            self.assertFalse((root / 'archive/manifests').exists())

    def test_corrupted_object_cannot_be_reused_or_restored(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.fixture(root); archive = root / 'archive'
            receipt = retain(root, archive)
            next((archive / 'objects').glob('*.gz')).write_bytes(b'corrupt')
            with self.assertRaises(ValueError): retain(root, archive)
            with self.assertRaises(ValueError): restore(archive, receipt['manifestSha256'], root / 'restored')

    def test_untrusted_manifest_identity_cannot_select_another_path(self):
        with tempfile.TemporaryDirectory() as folder:
            for identity in ('../outside', 'A' * 64, ''):
                with self.assertRaises(ValueError): restore(Path(folder), identity, Path(folder) / 'target')

    def test_existing_valid_compression_is_reused_without_reencoding(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.fixture(root); archive = root / 'archive'
            raw = (root / 'data/games.csv').read_bytes()
            compressed = gzip.compress(raw, mtime=123)
            path = archive / 'objects' / (hashlib.sha256(raw).hexdigest() + '.gz')
            path.parent.mkdir(parents=True); path.write_bytes(compressed)
            receipt = retain(root, archive)
            self.assertEqual(path.read_bytes(), compressed)
            restore(archive, receipt['manifestSha256'], root / 'restored')


if __name__ == '__main__': unittest.main()
