import unittest
from scripts.red_zone_possessions import possession_rows


def row(pid, kind='pass', **changes):
    return {'play_id': str(pid), 'play_type': kind, 'touchdown': '0',
            'two_point_attempt': '0', 'extra_point_attempt': '0', **changes}


class PossessionPhases(unittest.TestCase):
    def test_unflagged_conversion_penalty_after_touchdown_is_excluded(self):
        plays = [row(1), row(2, touchdown='1'), row(3, 'no_play'), row(4, 'extra_point', extra_point_attempt='1')]
        self.assertEqual(possession_rows(plays), plays[:2])

    def test_defensive_touchdown_also_ends_original_possession(self):
        plays = [row(1, posteam='PIT', td_team='HOU', touchdown='1'),
                 row(2, 'no_play', posteam='HOU')]
        self.assertEqual(possession_rows(plays), plays[:1])

    def test_ordinary_penalty_remains_but_conversion_and_kickoff_do_not(self):
        plays = [row(1, 'kickoff'), row(2, 'no_play'), row(3, 'run'), row(4, two_point_attempt='1')]
        self.assertEqual(possession_rows(plays), plays[1:3])

    def test_source_row_order_is_preserved_when_play_ids_are_not_monotonic(self):
        plays = [row(3915, 'no_play'), row(3903, 'field_goal')]
        self.assertEqual(possession_rows(plays), plays)

    def test_nullified_play_can_have_unset_scoring_flags(self):
        play = row(1, 'no_play', touchdown='', two_point_attempt='', extra_point_attempt='')
        self.assertEqual(possession_rows([play]), [play])

    def test_duplicate_or_unknown_play_state_is_rejected(self):
        for plays in [[row(1), row(1)], [row(1, touchdown='')]]:
            with self.subTest(plays=plays), self.assertRaises(ValueError):
                possession_rows(plays)


if __name__ == '__main__': unittest.main()
