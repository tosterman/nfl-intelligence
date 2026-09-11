import copy
import gzip
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from personnel_schedule import verify_schedule

ROOT = Path(__file__).resolve().parents[1]


class PersonnelScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = json.loads((ROOT / 'data/site.json').read_bytes())
        # CI refreshes data/games.csv for other tests. Bind this regression to
        # the immutable source actually declared by the retained edition.
        digest = cls.site['source']['sha256']
        cls.raw = gzip.decompress((ROOT / 'data/forecast-input-archive/objects' / (digest + '.gz')).read_bytes())

    def test_real_edition_binds_every_game(self):
        result = verify_schedule(self.site, self.raw)
        self.assertEqual(set(result), {g['id'] for g in self.site['games']})

    def test_changed_schedule_bytes_fail_before_use(self):
        with self.assertRaisesRegex(ValueError, 'digest'):
            verify_schedule(self.site, self.raw + b'\n')

    def test_changed_or_duplicate_game_context_is_rejected(self):
        for field, value in [('kickoff', '2026-09-10T01:20:00+00:00'),
                             ('venue', 'Other Stadium'), ('neutral', True),
                             ('home', 'ATL'), ('week', 2)]:
            with self.subTest(field=field):
                altered = copy.deepcopy(self.site)
                altered['games'][0][field] = value
                with self.assertRaisesRegex(ValueError, 'context'):
                    verify_schedule(altered, self.raw)
        altered = copy.deepcopy(self.site)
        altered['games'].append(altered['games'][0])
        with self.assertRaisesRegex(ValueError, 'scope'):
            verify_schedule(altered, self.raw)

    def test_missing_game_is_rejected(self):
        altered = copy.deepcopy(self.site)
        altered['games'].pop()
        with self.assertRaisesRegex(ValueError, 'scope'):
            verify_schedule(altered, self.raw)
