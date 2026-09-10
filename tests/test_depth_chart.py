import sys, unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from depth_chart import quarterbacks_before

class DepthChartTests(unittest.TestCase):
    def setUp(self):
        self.cutoff=datetime(2026,9,10,12,tzinfo=timezone.utc)
        self.row={'dt':'2026-09-10T11:00:00Z','team':'CHI','pos_abb':'QB','pos_rank':'1','pos_grp_id':'21','pos_slot':'9','gsis_id':'player-1','player_name':'Example QB'}
    def select(self,rows):return quarterbacks_before(rows,{'CHI'},self.cutoff)['CHI']
    def test_future_and_equal_cutoff_cannot_change_prior_role(self):
        for at in ['2026-09-10T12:00:00Z','2026-09-10T13:00:00Z']:
            result=self.select([self.row,self.row|{'dt':at,'gsis_id':'future'}])
            self.assertEqual(result['listedFirst'],'player-1')
    def test_newer_snapshot_without_qb_does_not_reuse_old_qb(self):
        newer=self.row|{'dt':'2026-09-10T11:30:00Z','pos_abb':'WR'}
        for rows in [[self.row,newer],[newer,self.row]]:
            self.assertEqual(self.select(rows)['status'],'unavailable')
    def test_duplicate_rank_missing_id_and_conflicting_formations_withheld(self):
        for rows in [[self.row,self.row], [self.row|{'gsis_id':''}], [self.row,self.row|{'pos_grp_id':'22','gsis_id':'other'}], [self.row,self.row|{'pos_rank':'2'}]]:
            self.assertEqual(self.select(rows)['status'],'unavailable')
    def test_stale_and_absent_teams_withheld(self):
        self.assertEqual(self.select([])['status'],'unavailable')
        self.assertEqual(self.select([self.row|{'dt':(self.cutoff-timedelta(hours=30)).isoformat()}])['status'],'unavailable')
    def test_unordered_rows_use_latest_snapshot(self):
        newer=self.row|{'dt':'2026-09-10T11:30:00Z','gsis_id':'new'}
        self.assertEqual(self.select([newer,self.row])['listedFirst'],'new')

if __name__=='__main__':unittest.main()
