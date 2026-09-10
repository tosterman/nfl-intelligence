import sys,unittest
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_personnel_identity import reconcile_reports,report_scope
NOW=datetime(2026,9,10,12,tzinfo=timezone.utc)
def row(team='A',player='p',name='Player',at='2026-09-10T11:00:00Z'):
    return {'team':team,'gsis_id':player,'player_name':name,'dt':at}
PLAYER={'playerId':'p','name':'Player','team':'A'}
class PersonnelIdentityTests(unittest.TestCase):
    def test_multiple_report_weeks_require_separate_temporal_audits(self):
        row={'season':2026,'type':'REG','week':1}
        self.assertEqual(report_scope([row,row]),row)
        for rows in [[],[row,{**row,'week':2}]]:
            with self.assertRaises(ValueError):report_scope(rows)
    def test_match_absence_conflict_and_ambiguity_remain_distinct(self):
        cases=[([row()],'matched'),([row(player='other',name='Other')],'not-listed'),([row(player='other'),row(team='B')],'team-conflict'),([row(),row(team='B')],'ambiguous-teams'),([row(name='Other spelling')],'name-variant'),([row(),row(name='Other spelling')],'ambiguous-names')]
        for rows,status in cases:
            with self.subTest(status=status):self.assertEqual(reconcile_reports([PLAYER],rows,NOW)[0]['status'],status)
    def test_newest_snapshot_wins_without_old_player_fallback(self):
        rows=[row(),row(player='replacement',name='Replacement',at='2026-09-10T11:30:00Z')]
        self.assertEqual(reconcile_reports([PLAYER],rows,NOW)[0]['status'],'not-listed')
        for at in ['2026-09-09T06:00:00Z','2026-09-10T12:00:00Z','2026-09-11T00:00:00Z']:
            self.assertEqual(reconcile_reports([PLAYER],[row(at=at)],NOW)[0]['status'],'source-unavailable')
    def test_duplicate_roles_on_same_team_are_not_multiple_team_conflicts(self):
        self.assertEqual(reconcile_reports([PLAYER],[row(),row()],NOW)[0]['status'],'matched')
    def test_same_name_candidate_never_silently_merges_different_identifiers(self):
        result=reconcile_reports([PLAYER],[row(player='alternative-id')],NOW)[0]
        self.assertEqual(result['status'],'identifier-mismatch')
        self.assertEqual(result['depthTeams'],[])
        self.assertEqual(result['sameNameCandidates'],[{'playerId':'alternative-id','name':'Player'}])

if __name__=='__main__':unittest.main()
