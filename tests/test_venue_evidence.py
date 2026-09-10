import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from venue_evidence import validate_venue
ROOT=Path(__file__).resolve().parents[1]

class VenueEvidenceTests(unittest.TestCase):
    def test_every_published_census_point_matches_its_evidence(self):
        venues=json.loads((ROOT/'data/weather-venues.json').read_text())
        self.assertTrue(any(v.get('status')=='confirmed-address-geocode' for v in venues.values()))
        for name,venue in venues.items():
            with self.subTest(venue=name):validate_venue(venue)

    def test_single_fuzzy_match_is_not_sufficient(self):
        record=json.loads((ROOT/'reviews/weather-location-followup.json').read_text())[0]
        point=record['geocodeMatches'][0]['coordinates']
        venue=record|{'status':'confirmed-address-geocode','latitude':point['y'],'longitude':point['x']}
        with self.assertRaisesRegex(ValueError,'address'):validate_venue(venue)

    def test_coordinate_drift_and_duplicate_match_fail(self):
        venue=next(v for v in json.loads((ROOT/'data/weather-venues.json').read_text()).values() if v.get('status')=='confirmed-address-geocode')
        with self.assertRaisesRegex(ValueError,'coordinates'):validate_venue(venue|{'latitude':venue['latitude']+.1})
        with self.assertRaises(ValueError):validate_venue(venue|{'geocodeMatches':venue['geocodeMatches']*2})
