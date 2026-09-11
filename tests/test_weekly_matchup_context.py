import copy
import unittest
from scripts.weekly_matchup_context import weekly_context
from test_red_zone_publication import GAME, plays


def fixture():
    schedule = [{**GAME, 'season': '2025', 'week': str(week), 'game_type': 'REG',
                 'game_id': f'2025_0{week}_BUF_NYJ', 'gameday': f'2025-09-{day:02d}'}
                for week, day in [(1, 7), (2, 14), (3, 21)]]
    rows = [{**row, 'game_id': game['game_id'], 'game_date': game['gameday'],
             'yards_gained': '20', 'qb_kneel': '0', 'qb_spike': '0'}
            for game in schedule for row in plays()]
    rows += [{'game_id': game['game_id'], 'game_date': game['gameday'], 'play_id': '3',
              'play_type': '', 'desc': 'END GAME', 'fixed_drive': '3',
              'total_home_score': game['home_score'], 'total_away_score': game['away_score']}
             for game in schedule]
    return schedule, rows


class WeeklyMatchupContext(unittest.TestCase):
    def test_week_boundaries_keep_sample_counts_and_denominators(self):
        schedule, rows = fixture()
        for week, count in [(1, 0), (2, 1), (3, 2)]:
            result = weekly_context(rows, schedule, 2025, week, 'REG')
            self.assertEqual(len(result['gameIds']), count)
            self.assertEqual(result['status'], 'available' if count else 'no-eligible-games')
            if count:
                self.assertEqual(result['teams']['BUF']['offense']['passing'], {'plays': count, 'explosive': count})
                self.assertEqual(result['teams']['BUF']['offense']['inside20'], {'possessions': count, 'touchdowns': count})
                self.assertEqual(result['teams']['NYJ']['defense']['inside20'], {'possessions': count, 'touchdowns': count})

    def test_same_week_and_later_results_cannot_change_earlier_context(self):
        schedule, rows = fixture()
        baseline = weekly_context(rows, schedule, 2025, 2, 'REG')
        changed = copy.deepcopy(rows)
        for row in changed:
            if row['game_id'] != schedule[0]['game_id']:
                row['yards_gained'] = '80'
                row['touchdown'] = '1'
        self.assertEqual(baseline, weekly_context(changed, schedule, 2025, 2, 'REG'))
        # A later week listed unusually early is still not eligible.
        schedule[2]['gameday'] = '2025-09-01'
        self.assertEqual(baseline, weekly_context(changed, schedule, 2025, 2, 'REG'))

    def test_missing_prior_game_and_wrong_scope_fail(self):
        schedule, rows = fixture()
        with self.assertRaisesRegex(ValueError, 'coverage'):
            weekly_context(rows[1:], schedule, 2025, 2, 'REG')
        with self.assertRaisesRegex(ValueError, 'scope'):
            weekly_context(rows, schedule, 2025, 4, 'REG')

    def test_unfinished_prior_game_is_not_counted(self):
        schedule, rows = fixture()
        schedule[0]['home_score'] = ''
        self.assertEqual(weekly_context(rows, schedule, 2025, 2, 'REG')['status'], 'no-eligible-games')

    def test_partial_game_and_mismatched_terminal_scores_fail(self):
        schedule, rows = fixture()
        with self.assertRaisesRegex(ValueError, 'terminal coverage'):
            weekly_context([r for r in rows if r.get('desc') != 'END GAME'], schedule, 2025, 2, 'REG')
        for row in rows:
            if row.get('desc') == 'END GAME':
                row['total_home_score'] = '0'
        with self.assertRaisesRegex(ValueError, 'Terminal score'):
            weekly_context(rows, schedule, 2025, 2, 'REG')

    def test_postseason_keeps_prior_regular_games_separate_from_postseason_week(self):
        schedule, rows = fixture()
        schedule[2]['game_type'] = 'POST'
        schedule[2]['week'] = '1'
        result = weekly_context(rows, schedule, 2025, 1, 'POST')
        self.assertEqual(result['gameIds'], [schedule[0]['game_id'], schedule[1]['game_id']])

    def test_play_ids_are_identity_not_chronological_order(self):
        schedule, rows = fixture()
        rows[0]['play_id'] = '100'
        self.assertEqual(len(weekly_context(rows, schedule, 2025, 2, 'REG')['gameIds']), 1)
        terminal = next(r for r in rows if r.get('desc') == 'END GAME')
        rows.remove(terminal)
        rows.insert(0, terminal)
        with self.assertRaisesRegex(ValueError, 'terminal play ordering'):
            weekly_context(rows, schedule, 2025, 2, 'REG')


if __name__ == '__main__':
    unittest.main()
