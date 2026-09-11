import copy
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from official_map_evidence import validate_candidate
from refresh_weather import acquire_game
from datetime import datetime, timezone, timedelta

class OfficialMapEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.c = json.loads((ROOT / 'reviews/highmark-official-map-candidate.json').read_text())
        self.raw = {key: gzip.decompress((ROOT / 'data/weather-location-sources' / (self.c[key] + ('.html.gz' if key == 'officialHtmlHash' else '.json.gz'))).read_bytes())
                    for key in ('officialHtmlHash', 'locationsHash', 'osmResponseHash', 'pointHash')}

    def test_complete_retained_chain(self):
        validate_candidate(self.c, self.raw)

    def test_wrong_point_season_and_address_claim_rejected(self):
        for key, value in [('latitude', 42.773), ('validFromSeason', 2025), ('addressStatus', 'matched'), ('officialMapUrl', 'https://map.concept3d.com/?id=1'), ('pointState', 'PA')]:
            with self.subTest(key=key):
                c = copy.deepcopy(self.c); c[key] = value
                with self.assertRaises(ValueError): validate_candidate(c, self.raw)

    def test_corrupt_source_and_wrong_named_entrance_rejected(self):
        raw = dict(self.raw); raw['locationsHash'] = b'[]'
        with self.assertRaisesRegex(ValueError, 'fingerprint'): validate_candidate(self.c, raw)
        for field, value in [('lat', 0), ('id', 1), ('mapId', 1)]:
            c = copy.deepcopy(self.c); data = json.loads(self.raw['locationsHash'])
            category = next(r for r in data if r.get('catId') == 107420)
            category['children']['locations'][0][field] = value
            raw = dict(self.raw); raw['locationsHash'] = json.dumps(data).encode()
            c['locationsHash'] = hashlib.sha256(raw['locationsHash']).hexdigest()
            with self.subTest(field=field), self.assertRaises(ValueError): validate_candidate(c, raw)

    def test_old_highmark_season_never_requests_weather(self):
        now = datetime.now(timezone.utc)
        venue = {'Highmark Stadium': {'validFromSeason': 2026, 'latitude': self.c['latitude'], 'longitude': self.c['longitude']}}
        def forbidden(url): raise AssertionError('No request for unqualified season')
        for season in (2025, None):
            game = {'id': 'g', 'season': season, 'kickoff': (now + timedelta(days=1)).isoformat(), 'venue': 'Highmark Stadium'}
            self.assertEqual(acquire_game(game, venue, now, forbidden)['reason'], 'Verified venue location does not cover this season')
