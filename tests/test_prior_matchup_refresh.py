import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime
from scripts.refresh_weekly_matchup import acquire
from scripts.refresh_prior_matchup import run
from scripts.refresh_weekly_matchup import encode
from scripts.weekly_matchup_context import from_retained

NOW = '2026-09-11T14:00:00+00:00'


class PriorRefresh(unittest.TestCase):
    def test_successful_current_capture_replays_exactly(self):
        root = Path(__file__).resolve().parents[1]
        collection = json.loads((root / 'data/prior-matchup-collection.json').read_text())
        if collection['status'] != 'ok':
            self.skipTest('Latest historical acquisition was unavailable')
        raw = (root / f"data/weekly-matchup-sources/{collection['manifestHash']}.manifest.json").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), collection['manifestHash'])
        manifest = json.loads(raw)
        corrections = json.loads((root / 'data/red-zone-adjudications.json').read_text())
        if corrections['sourceSha256'] != manifest['plays']['sha256']:
            corrections = {'sourceSha256': manifest['plays']['sha256'], 'decisions': []}
        result = from_retained(root, manifest, corrections, forecast_season=collection['forecastSeason'])
        self.assertEqual(hashlib.sha256(encode(result)).hexdigest(), collection['artifactSha256'])
        self.assertEqual(result, json.loads((root / 'data/prior-matchup-context.json').read_text()))

    def provider(self, calls, schedule_time='2026-09-11T13:00:00Z'):
        files = {'play_by_play_2025.csv.gz': gzip.compress(b'example', mtime=0), 'games.csv': b'schedule'}
        def read(url):
            calls.append(url)
            if '/releases/tags/' in url:
                tag = url.rsplit('/', 1)[-1]
                name = 'games.csv' if tag == 'schedules' else 'play_by_play_2025.csv.gz'
                raw = files[name]
                return json.dumps({'assets': [{'name': name, 'size': len(raw),
                    'updated_at': schedule_time if tag == 'schedules' else '2026-08-13T12:00:00Z',
                    'browser_download_url': f'https://github.com/nflverse/nflverse-data/releases/download/{tag}/{name}',
                    'digest': 'sha256:' + hashlib.sha256(raw).hexdigest()}]}).encode()
            return files[url.rsplit('/', 1)[-1]]
        return read

    def test_old_historical_plays_are_reused_but_schedule_must_be_fresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            calls = []
            read = self.provider(calls)
            clock = lambda: datetime.fromisoformat(NOW)
            manifest, _ = acquire(root, 2025, NOW, read, clock, historical=True)
            calls.clear()
            acquire(root, 2025, NOW, read, clock, historical=True)
            self.assertFalse(any('/download/pbp/' in url for url in calls))
            with self.assertRaises(ValueError):
                acquire(root, 2025, NOW, self.provider([], '2026-08-13T12:00:00Z'), clock, historical=True)
            (root / manifest['plays']['path']).write_bytes(b'corrupt')
            with self.assertRaises(ValueError):
                acquire(root, 2025, NOW, read, clock, historical=True)

    def test_failed_refresh_preserves_verified_sample(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            (root / 'data/site.json').write_text('{"season":2026}')
            sample = root / 'data/prior-matchup-context.json'
            sample.write_bytes(b'previous verified sample')
            def fail(url):
                raise OSError('offline')
            self.assertEqual(run(root, fail, lambda: datetime.fromisoformat(NOW)), 1)
            self.assertEqual(sample.read_bytes(), b'previous verified sample')
            self.assertEqual(json.loads((root / 'data/prior-matchup-collection.json').read_text())['status'], 'unavailable')
