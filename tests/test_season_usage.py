import sys
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from season_usage import season_usage


class SeasonUsage(unittest.TestCase):
    def setUp(self):
        self.cutoff = datetime(2026, 9, 17, tzinfo=timezone.utc)
        self.registry = [{'gsis_id': 'g', 'pfr_id': 'p'}]
        self.games = {'week1': {'season': 2026, 'week': 1, 'type': 'REG',
            'kickoff': self.cutoff-timedelta(days=7), 'teams': ['A', 'B'], 'completed': True}}
        self.row = {'game_id': 'week1', 'season': '2026', 'week': '1', 'game_type': 'REG',
            'pfr_player_id': 'p', 'team': 'A', 'opponent': 'B', 'offense_pct': '.5',
            'defense_pct': '0', 'st_pct': '.1', 'offense_snaps': '30', 'defense_snaps': '0', 'st_snaps': '2'}

    def usage(self, rows=None, **changes):
        args = dict(gsis_id='g', registry=self.registry, snaps=rows if rows is not None else [self.row],
                    games=self.games, cutoff=self.cutoff, season=2026, kind='REG', week=2, current_team='B')
        return season_usage(**(args | changes))

    def test_same_week_and_later_never_enter_earlier_context(self):
        self.assertEqual(self.usage(week=1)['overall']['status'], 'unavailable')
        self.assertEqual(self.usage()['overall']['appearances'], 1)
        self.games['week1']['week'] = 3
        self.assertEqual(self.usage()['overall']['status'], 'unavailable')

    def test_transfer_and_missing_rows_do_not_imply_zero(self):
        result = self.usage()
        self.assertEqual(result['formerTeams']['appearances'], 1)
        self.assertEqual(result['currentTeam']['status'], 'unavailable')
        self.assertEqual(result['overall']['historicalTeams'], ['A'])
        self.assertEqual(self.usage([])['overall']['status'], 'unavailable')

    def test_source_scope_and_completion_embargo(self):
        with self.assertRaises(ValueError): self.usage([{**self.row, 'week': '2'}])
        with self.assertRaises(ValueError): self.usage([{**self.row, 'season': '2025'}])
        self.games['week1']['completed'] = False
        self.assertEqual(self.usage()['overall']['status'], 'unavailable')
        self.games['week1']['completed'] = True
        self.games['week1']['kickoff'] = self.cutoff-timedelta(hours=24)
        self.assertEqual(self.usage()['overall']['status'], 'unavailable')

    def test_postseason_can_use_regular_season_but_not_reverse(self):
        self.assertEqual(self.usage(kind='POST', week=1)['overall']['appearances'], 1)
        self.games['week1']['type'] = 'POST'
        row = {**self.row, 'game_type': 'POST'}
        self.assertEqual(self.usage([row])['overall']['status'], 'unavailable')

    def test_ambiguous_identity_withholds_all_partitions(self):
        self.registry.append({'gsis_id': 'other', 'pfr_id': 'p'})
        result = self.usage()
        self.assertTrue(all(result[k]['status'] == 'unavailable' for k in ('overall','currentTeam','formerTeams')))
