import unittest
from scripts.explosive_plays import summarize


GAME = {'game_id': '2025_01_BUF_NYJ', 'gameday': '2025-09-07',
        'home_team': 'NYJ', 'away_team': 'BUF', 'home_score': '10', 'away_score': '20'}


def play(pid, kind='pass', yards='20', **changes):
    return dict(game_id=GAME['game_id'], game_date=GAME['gameday'],
                play_id=str(pid), posteam='BUF', defteam='NYJ',
                play_type=kind, yards_gained=yards, qb_kneel='0', qb_spike='0', **changes)


class ExplosivePlays(unittest.TestCase):
    def test_thresholds_and_denominators_include_sacks_and_scrambles(self):
        result = summarize([play(1), play(2, yards='19'), play(3, yards='-8'),
                            play(4, 'run', '10'), play(5, 'run', '9'),
                            play(6, 'no_play', '80'), play(7, 'qb_kneel', '-1')], [GAME], '2025-09-08')
        self.assertEqual(result[0]['passing'], {'plays': 3, 'explosive': 1})
        self.assertEqual(result[0]['rushing'], {'plays': 2, 'explosive': 1})
        self.assertEqual(result[0]['offense'], 'BUF')
        self.assertEqual(result[0]['defense'], 'NYJ')

    def test_cutoff_is_strict_and_unfinished_games_do_not_qualify(self):
        self.assertEqual(summarize([play(1)], [GAME], GAME['gameday']), [])
        self.assertEqual(summarize([play(1)], [{**GAME, 'home_score': ''}], '2025-09-08'), [])

    def test_duplicate_or_corrupt_evidence_is_rejected(self):
        for rows in [[play(1), play(1)], [play(1, yards='NaN')],
                     [{**play(1), 'defteam': 'BUF'}], [{**play(1), 'game_date': '2025-09-06'}],
                     [{**play(1), 'qb_spike': ''}]]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                summarize(rows, [GAME], '2025-09-08')

    def test_penalty_flag_does_not_discard_credited_play(self):
        self.assertEqual(summarize([play(1, penalty='1')], [GAME], '2025-09-08')[0]['passing'],
                         {'plays': 1, 'explosive': 1})

    def test_zero_denominator_is_retained_as_count_not_invented_rate(self):
        result = summarize([play(1, 'run', '0')], [GAME], '2025-09-08')
        self.assertEqual(result[0]['passing'], {'plays': 0, 'explosive': 0})


if __name__ == '__main__': unittest.main()
