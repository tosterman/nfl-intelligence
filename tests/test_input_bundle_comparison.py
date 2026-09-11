import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from forecast_input_archive import retain
from compare_input_bundles import compare_bundles
from refresh_input_comparison import remember, finish


def edition(root, time, score):
    (root / 'data/raw').mkdir(parents=True, exist_ok=True)
    raw = f'game_id,score\ng,{score}\n'.encode()
    stats = b'game_id,team,value\ng,DET,1\n'
    (root / 'data/games.csv').write_bytes(raw)
    (root / 'data/raw/stats_team_week_2025.csv').write_bytes(stats)
    site = {'generatedAt': time, 'source': {'sha256': hashlib.sha256(raw).hexdigest()},
            'efficiencySources': [{'season': 2025, 'sha256': hashlib.sha256(stats).hexdigest()}]}
    (root / 'data/site.json').write_text(json.dumps(site))


class InputBundleComparisonTests(unittest.TestCase):
    def test_exact_bundles_compare_and_repeating_is_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); archive = root / 'archive'
            edition(root, '2026-09-10T10:00:00Z', 7); before = retain(root, archive)['manifestSha256']
            edition(root, '2026-09-11T10:00:00Z', 10); after = retain(root, archive)['manifestSha256']
            result = compare_bundles(archive, before, after)
            self.assertEqual(result, compare_bundles(archive, before, after))
            self.assertEqual(result['beforeManifest'], before)
            self.assertEqual(result['afterManifest'], after)
            schedule = next(file for file in result['files'] if file['path'] == 'data/games.csv')
            self.assertEqual(schedule['revised'][0]['fields']['score'], {'before': '7', 'after': '10'})
            self.assertFalse(next(file for file in result['files'] if '/raw/' in file['path'])['recordsChanged'])
            with self.assertRaises(ValueError): compare_bundles(archive, after, before)

    def test_missing_corrupt_or_undated_bundle_cannot_be_compared(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); archive = root / 'archive'
            edition(root, '2026-09-10', 7); before = retain(root, archive)['manifestSha256']
            edition(root, '2026-09-11T10:00:00Z', 10); after = retain(root, archive)['manifestSha256']
            with self.assertRaises(ValueError): compare_bundles(archive, before, after)
            with self.assertRaises((ValueError, FileNotFoundError)): compare_bundles(archive, '0' * 64, after)

    def test_refresh_pairs_exact_pre_refresh_edition_and_reports_missing_history(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); archive = root / 'data/forecast-input-archive'
            edition(root, '2026-09-10T10:00:00Z', 7)
            remember(root)
            edition(root, '2026-09-11T10:00:00Z', 10); retain(root, archive)
            self.assertEqual(finish(root)['status'], 'previous-inputs-unavailable')
            edition(root, '2026-09-10T10:00:00Z', 7); retain(root, archive)
            remember(root)
            edition(root, '2026-09-11T10:00:00Z', 10)
            result = finish(root)
            self.assertEqual(result['status'], 'compared')
            self.assertEqual(len(list((archive / 'comparisons').glob('*.json'))), 1)

    def test_added_source_is_not_misrepresented_as_existing_record_revisions(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); archive = root / 'archive'
            edition(root, '2026-09-10T10:00:00Z', 7); before = retain(root, archive)['manifestSha256']
            edition(root, '2026-09-11T10:00:00Z', 7)
            raw = b'game_id,team,value\nnew,DET,2\n'
            (root / 'data/raw/stats_team_week_2026.csv').write_bytes(raw)
            site = json.loads((root / 'data/site.json').read_text())
            site['efficiencySources'].append({'season': 2026, 'sha256': hashlib.sha256(raw).hexdigest()})
            (root / 'data/site.json').write_text(json.dumps(site))
            after = retain(root, archive)['manifestSha256']
            result = compare_bundles(archive, before, after)
            self.assertEqual([entry['path'] for entry in result['addedSources']], ['data/raw/stats_team_week_2026.csv'])
            self.assertTrue(all(not file['recordsChanged'] for file in result['files']))

    def test_missing_prior_history_does_not_excuse_corrupt_current_bundle(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); archive = root / 'data/forecast-input-archive'
            edition(root, '2026-09-10T10:00:00Z', 7); remember(root)
            edition(root, '2026-09-11T10:00:00Z', 10); retain(root, archive)
            next((archive / 'objects').glob('*.gz')).write_bytes(b'corrupt')
            with self.assertRaises(ValueError): finish(root)


if __name__ == '__main__': unittest.main()
