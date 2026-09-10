import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_forecast_inputs import verify


class ForecastInputTests(unittest.TestCase):
    def test_matching_changed_and_missing_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / 'data/raw').mkdir(parents=True)
            schedule = root / 'data/games.csv'; stats = root / 'data/raw/stats_team_week_2026.csv'
            schedule.write_bytes(b'schedule'); stats.write_bytes(b'stats')
            site = {'generatedAt': '2026-09-10T00:00:00Z',
                    'source': {'sha256': hashlib.sha256(b'schedule').hexdigest()},
                    'efficiencySources': [{'season': 2026, 'sha256': hashlib.sha256(b'stats').hexdigest()}]}
            manifest = root / 'data/site.json'; manifest.write_text(json.dumps(site))
            self.assertTrue(verify(root)['inputsMatch'])
            schedule.write_bytes(b'new revision')
            self.assertFalse(verify(root)['files'][0]['matches'])
            stats.unlink()
            self.assertIsNone(verify(root)['files'][1]['actualSha256'])
            for season in ['../secret', True, 0]:
                site['efficiencySources'][0]['season'] = season
                manifest.write_text(json.dumps(site))
                with self.assertRaises(ValueError): verify(root)
            site['efficiencySources'][0]['season'] = 2026
            site['efficiencySources'] *= 2
            manifest.write_text(json.dumps(site))
            with self.assertRaises(ValueError): verify(root)
