import json,sys,unittest,gzip,hashlib,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from venue_evidence import validate_venue, stadium_name
ROOT=Path(__file__).resolve().parents[1]

class VenueEvidenceTests(unittest.TestCase):
    def test_retained_census_responses_match_recorded_results(self):
        venues=json.loads((ROOT/'data/weather-venues.json').read_text())
        captured=[v for v in venues.values() if v.get('geocodeHash')]
        self.assertTrue(captured)
        for venue in captured:
            with self.subTest(address=venue['address']):
                digest=venue['geocodeHash']
                raw=gzip.decompress((ROOT/'data/weather-location-sources'/(digest+'.json.gz')).read_bytes())
                self.assertEqual(hashlib.sha256(raw).hexdigest(),digest)
                result=json.loads(raw)['result']
                self.assertEqual(result['addressMatches'],venue['geocodeMatches'])
                self.assertEqual(result['input']['address']['address'],venue['address'])

    def test_osm_bounds_and_source_bytes_are_reproducible(self):
        for name,v in json.loads((ROOT/'data/weather-osm-venues.json').read_text()).items():
            validate_venue(v)
            for key in ['mapDataHash','pointHash']:
                raw=gzip.decompress((ROOT/'data/weather-location-sources'/(v[key]+'.json.gz')).read_bytes())
                self.assertEqual(hashlib.sha256(raw).hexdigest(),v[key])
                payload=json.loads(raw)
                if key=='mapDataHash':self.assertIn(v['mapElement'],payload['elements'])
                else:
                    self.assertEqual(payload['properties']['relativeLocation']['properties']['state'],v['pointState'])
                    self.assertEqual(payload['geometry']['type'],'Point')
                    self.assertEqual(payload['geometry']['coordinates'],[round(v['longitude'],4),round(v['latitude'],4)])
            self.assertEqual(stadium_name(v['mapElement']['tags']['name']),stadium_name(name))

    def test_osm_wrong_address_or_shifted_center_is_rejected(self):
        original=json.loads((ROOT/'data/weather-osm-venues.json').read_text())['Gillette Stadium']
        for field,value in [('latitude',0),('attribution',''),('pointState','FL')]:
            with self.assertRaises(ValueError):validate_venue(original|{field:value})
        changed=copy.deepcopy(original);changed['mapElement']['tags']['addr:street']='Patriot Circle'
        with self.assertRaisesRegex(ValueError,'address'):validate_venue(changed)

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

    def test_typographic_apostrophe_does_not_enable_fuzzy_matching(self):
        self.assertEqual(stadium_name("Levi\u2019s Stadium"), "Levi's Stadium")
        self.assertNotEqual(stadium_name("Levis Stadium"), "Levi's Stadium")
        self.assertNotEqual(stadium_name("Old Levi's Stadium"), "Levi's Stadium")
