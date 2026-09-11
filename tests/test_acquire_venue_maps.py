import io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import acquire_venue_maps as maps

class VenueMapAcquisitionTests(unittest.TestCase):
    def test_reviewed_us_bank_map_name_is_an_exact_alias(self):
        self.assertEqual(maps.map_name('U.S. Bank Stadium'),'US Bank Stadium')
        self.assertEqual(maps.map_name('Huntington Bank Stadium'),'Huntington Bank Stadium')
        self.assertEqual(maps.map_name('U S Bank Stadium'),'U S Bank Stadium')

    def test_timeout_remark_is_not_an_empty_success(self):
        payload={'elements':[],'remark':'runtime error: Query timed out'}
        with tempfile.TemporaryDirectory() as folder,patch.object(maps,'ROOT',Path(folder)),patch.object(maps,'urlopen',return_value=io.BytesIO(json.dumps(payload).encode())):
            with self.assertRaises(ValueError):maps.fetch('https://overpass-api.de/api/interpreter')
            self.assertFalse((Path(folder)/'data/weather-location-sources').exists())

    def test_unknown_or_duplicate_venue_does_not_make_network_requests(self):
        with patch.object(maps,'fetch',side_effect=AssertionError('Network must not be used')):
            for names in [[],['Not a configured venue'],['MetLife Stadium','MetLife Stadium']]:
                with self.assertRaises(ValueError):maps.main(names)
