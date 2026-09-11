import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from weather_bundle import build, ROOT


class WeatherBundleTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / 'data').mkdir()
        for name in ['site.json', 'weather.json', 'weather-history.json', 'weather-ledger.json', 'weather-venues.json', 'weather-osm-venues.json']:
            shutil.copyfile(ROOT / 'data' / name, self.root / 'data' / name)
        shutil.copytree(ROOT / 'data/weather-sources', self.root / 'data/weather-sources')

    def test_real_bundle_is_deterministic_and_binds_every_snapshot_game(self):
        first = build(self.root)
        self.assertEqual(first, build(self.root))
        self.assertEqual(set(first['payload']['contexts']), set(first['payload']['weather']['games']))
        self.assertGreater(len(first['manifest']['sourceHashes']), 0)

    def test_changed_schedule_rejects_previously_collected_weather(self):
        path = self.root / 'data/site.json'
        site = json.loads(path.read_bytes())
        weather = json.loads((self.root / 'data/weather.json').read_bytes())
        identity = next(k for k,v in weather['games'].items() if v['status'] == 'available')
        next(g for g in site['games'] if g['id'] == identity)['neutral'] = True
        path.write_text(json.dumps(site))
        with self.assertRaisesRegex(ValueError, 'context|venue'):
            build(self.root)

    def test_tampered_compact_history_is_rejected(self):
        path = self.root / 'data/weather-history.json'
        value = json.loads(path.read_bytes()); value['records'] = []
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'history'):
            build(self.root)
