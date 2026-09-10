import copy
import hashlib
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from publication_preflight import validate_forecast_edition


def fixture():
    context = dict(season=2026, week=1, type='REG', home='DAL', away='PHI',
                   kickoff='2026-09-12T00:00:00Z', venue='Stadium', neutral=False)
    snap = dict(gameId='g', generatedAt='2026-09-10T10:00:00Z', modelVersion='v1',
                gameContext=context, prediction={'homeMargin': 2})
    snap['hash'] = hashlib.sha256(json.dumps(snap, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    game = dict(context, id='g', status='scheduled', snapshot=snap, history=[snap])
    return dict(generatedAt='2026-09-10T12:00:00Z', season=2026, week=1,
                modelVersion='v1', games=[game]), [snap]


class PreflightTests(unittest.TestCase):
    def test_valid_and_equivalent_timezone(self):
        site, ledger = fixture()
        site['games'][0]['kickoff'] = '2026-09-11T20:00:00-04:00'
        self.assertEqual(validate_forecast_edition(site, ledger), 1)

    def test_rejects_unbound_changed_or_unarchived_display(self):
        for change in ('legacy', 'venue', 'ledger', 'history', 'wrong_game', 'future', 'model'):
            site, ledger = copy.deepcopy(fixture())
            game = site['games'][0]
            if change == 'legacy': game['snapshot'].pop('gameContext')
            if change == 'venue': game['venue'] = 'Different'
            if change == 'ledger': ledger = []
            if change == 'history': game['history'] = []
            if change == 'wrong_game': game['id'] = 'other'
            if change == 'future': site['generatedAt'] = '2026-09-10T09:00:00Z'
            if change == 'model': site['modelVersion'] = 'v2'
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_forecast_edition(site, ledger)

    def test_requires_current_week_future_games_but_not_final_or_later_week(self):
        site, ledger = fixture()
        site['games'][0]['snapshot'] = None
        with self.assertRaises(ValueError): validate_forecast_edition(site, ledger)
        site['games'][0]['week'] = 2
        self.assertEqual(validate_forecast_edition(site, ledger), 0)
        site['games'][0]['week'] = 1
        site['games'][0]['kickoff'] = '2026-09-09T00:00:00Z'
        site['games'][0]['status'] = 'final'
        self.assertEqual(validate_forecast_edition(site, ledger), 0)

    def test_duplicate_games_and_ledger_hashes_are_rejected(self):
        site, ledger = fixture()
        with self.assertRaises(ValueError): validate_forecast_edition(site, ledger * 2)
        site['games'] *= 2
        with self.assertRaises(ValueError): validate_forecast_edition(site, ledger)

    def test_future_edition_cannot_bypass_missing_forecast_requirement(self):
        site, ledger = fixture()
        site['generatedAt'] = '2099-01-01T00:00:00Z'
        site['games'][0]['snapshot'] = None
        with self.assertRaises(ValueError):
            validate_forecast_edition(site, ledger, now=datetime(2026, 9, 10, 13, tzinfo=timezone.utc))


if __name__ == '__main__': unittest.main()
