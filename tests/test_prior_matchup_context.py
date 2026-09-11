import copy
import unittest
from scripts.weekly_matchup_context import prior_season_context
from scripts.replay_prior_matchup_context import reconcile
from test_weekly_matchup_context import fixture


class PriorMatchupContext(unittest.TestCase):
    def fixture(self):
        schedule, rows = fixture()
        schedule[-1]['game_type'] = 'SB'
        schedule.append({**schedule[0], 'game_id': '2026_01_BUF_NYJ', 'season': '2026', 'gameday': '2026-09-10', 'home_score': '', 'away_score': ''})
        return schedule, rows

    def test_complete_prior_season_is_separate_from_unfinished_current_season(self):
        schedule, rows = self.fixture()
        result = prior_season_context(rows, schedule, 2026)
        self.assertEqual(result['season'], 2025)
        self.assertEqual(result['forecastSeason'], 2026)
        self.assertEqual(result['cutoff'], '2026-09-10')
        self.assertEqual(len(result['gameIds']), 3)
        self.assertEqual(result['teams']['BUF']['offense']['inside20'], {'possessions': 3, 'touchdowns': 3})
        self.assertNotIn('week', result)

    def test_incomplete_prior_scope_or_cross_season_dates_fail(self):
        for change in [{'home_score': ''}, {'game_type': 'CON'}, {'gameday': '2026-09-10'}]:
            schedule, rows = self.fixture()
            schedule[2].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                prior_season_context(rows, schedule, 2026)
        schedule, rows = self.fixture()
        with self.assertRaises(ValueError):
            prior_season_context(rows, schedule, 2027)
        with self.assertRaisesRegex(ValueError, 'coverage'):
            prior_season_context(rows[1:], schedule, 2026)

    def test_reconciliation_rejects_coverage_and_count_changes(self):
        counts = {'passing': {'plays': 10, 'explosive': 2},
                  'rushing': {'plays': 5, 'explosive': 1},
                  'inside20': {'possessions': 3, 'touchdowns': 2}, 'gameIds': ['g']}
        result = {'season': 2025, 'gameIds': ['g'],
                  'teams': {'BUF': {'offense': copy.deepcopy(counts), 'defense': copy.deepcopy(counts)}}}
        big = {'season': 2025, 'games': [{'gameId': 'g', 'offense': 'BUF', 'defense': 'BUF'}],
               'teams': {'BUF': {side: {kind: copy.deepcopy(counts[kind]) for kind in ('passing', 'rushing')}
                                 for side in ('offense', 'defense')}}}
        red = {'season': 2025, 'drives': [{'gameId': 'g'}],
               'teams': {'BUF': {side: copy.deepcopy(counts['inside20']) for side in ('offense', 'defense')}}}
        reconcile(result, big, red)
        variants = []
        changed = copy.deepcopy(result)
        changed['gameIds'] = []
        variants.append(changed)
        changed = copy.deepcopy(result)
        changed['teams'] = {}
        variants.append(changed)
        for side in ('offense', 'defense'):
            for kind, field in [('passing', 'explosive'), ('rushing', 'plays'), ('inside20', 'touchdowns')]:
                changed = copy.deepcopy(result)
                changed['teams']['BUF'][side][kind][field] += 1
                variants.append(changed)
            changed = copy.deepcopy(result)
            changed['teams']['BUF'][side]['gameIds'] = []
            variants.append(changed)
        for changed in variants:
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                reconcile(changed, big, red)


if __name__ == '__main__':
    unittest.main()
