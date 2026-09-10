import copy
import gzip
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from linked_place_evidence import validate_candidate


class LinkedPlaceEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.candidate = json.loads((ROOT / 'reviews/acrisure-linked-place-candidate.json').read_text(encoding='utf-8'))
        self.sources = {
            key: gzip.decompress((ROOT / 'data/weather-location-sources' / (self.candidate[key] + '.json.gz')).read_bytes())
            for key in ('osmResponseHash', 'pointHash')
        }

    def check(self, candidate):
        return validate_candidate(candidate, self.sources['osmResponseHash'], self.sources['pointHash'])

    def test_retained_candidate_is_consistent(self):
        self.check(self.candidate)

    def test_wrong_place_or_official_reference_is_rejected(self):
        mutations = [
            ('officialLinkSource', 'https://example.com/'),
            ('linkedPlaceUrl', 'https://www.waze.com/live-map/'),
            ('officialLinkPresent', False), ('placeLatitude', float('nan')),
            ('placeLongitude', -79), ('derivedLatitude', 40),
            ('pointState', 'OH'), ('forecastHourly', 'https://example.com/'),
            ('osmResponseHash', '0' * 64), ('pointHash', '0' * 64),
        ]
        for key, value in mutations:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check(self.candidate | {key: value})
        for field, value in [('name', 'Parking Lot'), ('addressRegion', 'Ohio'),
                             ('streetAddress', '900 Art Rooney Ave'), ('addressLocality', 'Philadelphia')]:
            changed = copy.deepcopy(self.candidate)
            target = changed['place'] if field == 'name' else changed['place']['address']
            target[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check(changed)

    def test_conflicting_or_duplicate_retained_geometry_is_rejected(self):
        import hashlib
        for conflict in ('address', 'duplicate'):
            changed = copy.deepcopy(self.candidate)
            payload = json.loads(self.sources['osmResponseHash'])
            element = next(e for e in payload['elements'] if e['id'] == changed['osmElement']['id'])
            if conflict == 'address':
                element['tags']['addr:street'] = 'Wrong Road'
                changed['osmElement'] = element
            else:
                payload['elements'].append(copy.deepcopy(element))
            raw = json.dumps(payload).encode()
            changed['osmResponseHash'] = hashlib.sha256(raw).hexdigest()
            with self.subTest(conflict=conflict), self.assertRaises(ValueError):
                validate_candidate(changed, raw, self.sources['pointHash'])

    def test_rehashed_nws_response_still_requires_midpoint_and_state(self):
        import hashlib
        for field in ('coordinates', 'state', 'forecastHourly'):
            changed = copy.deepcopy(self.candidate)
            payload = json.loads(self.sources['pointHash'])
            if field == 'coordinates':
                payload['geometry']['coordinates'][0] += .01
            elif field == 'state':
                payload['properties']['relativeLocation']['properties']['state'] = 'OH'
            else:
                payload['properties']['forecastHourly'] = 'https://api.weather.gov/gridpoints/PBZ/78,66/forecast/hourly'
                changed['forecastHourly'] = payload['properties']['forecastHourly']
            raw = json.dumps(payload).encode()
            changed['pointHash'] = hashlib.sha256(raw).hexdigest()
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_candidate(changed, self.sources['osmResponseHash'], raw)


if __name__ == '__main__':
    unittest.main()
