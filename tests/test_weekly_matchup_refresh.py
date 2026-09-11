import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timezone
from scripts.refresh_weekly_matchup import acquire, run, save_current
from scripts.weekly_matchup_context import from_retained

NOW = '2026-09-11T14:00:00+00:00'


def provider(bad_digest=False, updated='2026-09-11T13:00:00Z'):
    files = {'play_by_play_2026.csv.gz': gzip.compress(b'example', mtime=0), 'games.csv': b'schedule'}
    def read(url):
        if '/releases/tags/' in url:
            tag = url.rsplit('/', 1)[-1]
            name = 'games.csv' if tag == 'schedules' else 'play_by_play_2026.csv.gz'
            raw = files[name]
            return json.dumps({'assets': [{'name': name, 'size': len(raw), 'updated_at': updated,
                'browser_download_url': f'https://github.com/nflverse/nflverse-data/releases/download/{tag}/{name}',
                'digest': 'sha256:' + ('0' * 64 if bad_digest else hashlib.sha256(raw).hexdigest())}]}).encode()
        return files[url.rsplit('/', 1)[-1]]
    return read


class WeeklyRefresh(unittest.TestCase):
    def test_current_snapshot_reproduces_from_retained_inputs(self):
        root = Path(__file__).resolve().parents[1]
        current = json.loads((root / 'data/weekly-matchup-context.json').read_text())
        if current['status'] == 'unavailable':
            self.assertNotIn('currentSeason', current)
            return
        raw = (root / f"data/weekly-matchup-sources/{current['manifestHash']}.manifest.json").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), current['manifestHash'])
        manifest = json.loads(raw)
        corrections = json.loads((root / 'data/red-zone-adjudications.json').read_text())
        if corrections['sourceSha256'] != manifest['plays']['sha256']:
            corrections = {'sourceSha256': manifest['plays']['sha256'], 'decisions': []}
        result = from_retained(root, manifest, corrections, current['week'], current['currentSeason']['gameType'])
        self.assertEqual(result, current['currentSeason'])

    def test_source_capture_is_immutable_and_metadata_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clock = lambda: datetime.fromisoformat(NOW)
            manifest, identity = acquire(root, 2026, NOW, provider(), clock)
            self.assertEqual((manifest, identity), acquire(root, 2026, NOW, provider(), clock))
            source = root / manifest['plays']['path']
            source.write_bytes(b'corrupt')
            with self.assertRaises(ValueError):
                acquire(root, 2026, NOW, provider())

    def test_bad_digest_and_stale_or_future_source_cannot_publish_manifest(self):
        for read in [provider(True), provider(updated='2026-09-08T13:00:00Z'), provider(updated='2026-09-12T13:00:00Z')]:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with self.assertRaises(ValueError):
                    acquire(root, 2026, NOW, read)
                self.assertEqual(list(root.rglob('*.manifest.json')), [])

    def test_failure_preserves_previous_archive_and_marks_current_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            (root / 'data/site.json').write_text(json.dumps({'season': 2026, 'week': 1,
                'games': [{'season': 2026, 'week': 1, 'type': 'REG'}]}))
            save_current(root, {'status': 'ok', 'older': True})
            old_archives = {p: p.read_bytes() for p in root.rglob('*.snapshot.json')}
            code = run(root, provider(True), lambda: datetime(2026, 9, 11, 14, tzinfo=timezone.utc))
            self.assertEqual(code, 1)
            current = json.loads((root / 'data/weekly-matchup-context.json').read_text())
            self.assertEqual(current['status'], 'unavailable')
            self.assertNotIn('currentSeason', current)
            self.assertTrue(all(p.read_bytes() == raw for p, raw in old_archives.items()))


if __name__ == '__main__':
    unittest.main()
