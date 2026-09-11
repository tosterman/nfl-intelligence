import unittest
import json
from pathlib import Path
from scripts.build_red_zone_evidence import summarize_drives, build

GAME = {'game_id': '2025_01_BUF_NYJ', 'gameday': '2025-09-07', 'home_team': 'NYJ',
        'away_team': 'BUF', 'home_score': '10', 'away_score': '20'}


def plays():
    return [{'game_id': GAME['game_id'], 'game_date': GAME['gameday'], 'play_id': str(i),
             'fixed_drive': str(i), 'posteam': offense, 'defteam': defense,
             'play_type': 'pass', 'yardline_100': '10', 'touchdown': td,
             'td_team': offense if td == '1' else '', 'two_point_attempt': '0',
             'extra_point_attempt': '0', 'fixed_drive_result': result}
            for i, offense, defense, td, result in [(1, 'BUF', 'NYJ', '1', 'Touchdown'),
                                                   (2, 'NYJ', 'BUF', '0', 'End of half')]]


class Publication(unittest.TestCase):
    def test_retained_artifact_replays_with_balanced_offense_defense_counts(self):
        root = Path(__file__).resolve().parents[1]
        result = build(root)
        self.assertEqual(result, json.loads((root / 'data/red-zone.json').read_text()))
        self.assertEqual(len({r['gameId'] for r in result['drives']}), 285)
        self.assertEqual(len(result['teams']), 32)
        for field, total in [('possessions', 1824), ('touchdowns', 1046)]:
            for side in ['offense', 'defense']:
                self.assertEqual(sum(t[side][field] for t in result['teams'].values()), total)
        sample = [r for r in result['drives'] if r['gameId'] == '2025_03_CIN_MIN' and r['inside20']]
        self.assertEqual([(team, sum(r['offensiveTouchdown'] for r in sample if r['offense'] == team),
                           sum(r['offense'] == team for r in sample)) for team in ['CIN', 'MIN']],
                         [('CIN', 1, 1), ('MIN', 4, 5)])

    def test_both_offenses_are_counted_and_cutoff_is_strict(self):
        result = summarize_drives(plays(), [GAME], '2025-09-08', 2025)
        self.assertEqual(sum(r['inside20'] for r in result), 2)
        self.assertEqual(sum(r['offensiveTouchdown'] for r in result), 1)
        self.assertEqual(summarize_drives(plays(), [GAME], GAME['gameday'], 2025), [])
        self.assertEqual(summarize_drives(plays(), [{**GAME, 'home_score': ''}], '2025-09-08', 2025), [])

    def test_missing_offense_and_mismatched_game_context_are_rejected(self):
        variants = [plays()[:1], [{**r, 'game_date': '2025-09-06'} for r in plays()],
                    [{**r, 'posteam': 'NE'} for r in plays()], plays() + plays()[:1]]
        for rows in variants:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                summarize_drives(rows, [GAME], '2025-09-08', 2025)


if __name__ == '__main__': unittest.main()
