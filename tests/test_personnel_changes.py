import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from personnel_changes import changes


class PersonnelChangesTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(season=2026, type='REG', week=1, team='CHI', playerId='00-0030000', name='Example', position='QB', reportStatus='Questionable')
        self.before = {'retrievedAt':'2026-09-10T12:00:00Z', 'players':[self.row]}
        self.after = {'retrievedAt':'2026-09-10T13:00:00Z', 'players':[self.row.copy()]}

    def test_identical_redownload_is_not_a_player_change(self):
        self.assertEqual(changes(self.before,self.after),[])

    def test_change_preserves_unknown_event_time(self):
        self.after['players'][0]['reportStatus']='Out'
        result=changes(self.before,self.after)[0]
        self.assertEqual(result['kind'],'changed')
        self.assertIsNone(result['eventTime'])
        self.assertEqual(result['fields'],{'reportStatus':{'before':'Questionable','after':'Out'}})

    def test_disappearance_does_not_become_cleared(self):
        self.after['players']=[]
        self.assertEqual(changes(self.before,self.after)[0]['kind'],'no-longer-present')

    def test_week_or_identifier_change_never_silently_joins(self):
        for key,value in [('week',2),('playerId','00-0099999'),('team','CAR')]:
            after=self.after | {'players':[self.row | {key:value}]}
            self.assertEqual(sorted(r['kind'] for r in changes(self.before,after)),['first-observed','no-longer-present'])

    def test_duplicate_and_nonmonotonic_captures_rejected(self):
        with self.assertRaises(ValueError): changes(self.before,self.before)
        with self.assertRaises(ValueError): changes(self.after,self.before)
        with self.assertRaises(ValueError): changes(self.before,self.after | {'players':[self.row,self.row]})
