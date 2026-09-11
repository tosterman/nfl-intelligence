import unittest
from scripts.red_zone_possessions import drive_evidence


def row(pid, yards, **changes):
    return {'play_id': str(pid), 'play_type': 'pass', 'touchdown': '0',
            'two_point_attempt': '0', 'extra_point_attempt': '0',
            'posteam': 'BUF', 'defteam': 'NYJ', 'yardline_100': str(yards),
            'td_team': '', 'fixed_drive_result': 'Touchdown', **changes}


class RedZoneOutcomes(unittest.TestCase):
    def test_one_trip_can_move_outside_twenty_before_scoring(self):
        result = drive_evidence([row(1, 15), row(2, 30), row(3, 30, touchdown='1', td_team='BUF')])
        self.assertTrue(result['inside20'])
        self.assertTrue(result['offensiveTouchdown'])
        self.assertEqual(result['entryPlayId'], '1')

    def test_defensive_return_is_not_offensive_conversion(self):
        result = drive_evidence([row(1, 10, touchdown='1', td_team='NYJ', fixed_drive_result='Opp touchdown')])
        self.assertTrue(result['inside20'])
        self.assertFalse(result['offensiveTouchdown'])

    def test_punt_return_score_reconciles_without_offensive_touchdown(self):
        result = drive_evidence([row(1, 90, fixed_drive_result='Opp touchdown'),
            row(2, 90, play_type='punt', touchdown='1', td_team='NYJ', fixed_drive_result='Opp touchdown')])
        self.assertFalse(result['offensiveTouchdown'])
        self.assertFalse(result['inside20'])

    def test_exact_twenty_and_long_touchdown_do_not_invent_inside_twenty_snap(self):
        result = drive_evidence([row(1, 20, touchdown='1', td_team='BUF'), row(2, 2, two_point_attempt='1')])
        self.assertFalse(result['inside20'])

    def test_conflicting_result_and_unknown_scoring_team_are_rejected(self):
        for plays in [[row(1, 10)], [row(1, 10, touchdown='1')]]:
            with self.subTest(plays=plays), self.assertRaises(ValueError):
                drive_evidence(plays)


if __name__ == '__main__': unittest.main()
