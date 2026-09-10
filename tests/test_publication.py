import sys,unittest
from pathlib import Path
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from publication import eligible_snapshot,grade_prospective,verify_append_only
from refresh import digest

class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.game={'id':'g','kickoff':'2026-09-10T20:00:00+00:00','status':'final','actualHome':24,'actualAway':21}
        self.snap={'gameId':'g','hash':'a','generatedAt':'2026-09-10T10:00:00+00:00','prediction':{'homeWinProbability':.6,'homeMargin':3,'total':45}}
        self.snap['hash']=digest({k:v for k,v in self.snap.items() if k!='hash'})
    def test_local_generation_is_not_publication(self):
        self.assertIsNone(eligible_snapshot(self.game,[self.snap],[]))
    def test_failed_or_postkickoff_publication_not_eligible(self):
        for status,at in [('failed','2026-09-10T11:00:00+00:00'),('ready','2026-09-10T21:00:00+00:00')]:
            self.assertIsNone(eligible_snapshot(self.game,[self.snap],[{'status':status,'publishedAt':at,'snapshotHashes':['a'],'deploymentUrl':'https://example.vercel.app'}]))
    def test_valid_receipt_scores_original_prediction(self):
        receipts=[{'status':'ready','publishedAt':'2026-09-10T11:00:00+00:00','snapshotHashes':[self.snap['hash']],'deploymentUrl':'https://example.vercel.app'}]
        result=grade_prospective([self.game],[self.snap],receipts)
        self.assertEqual(result['games'],1);self.assertEqual(result['wins'],1);self.assertAlmostEqual(result['brier'],.16)
    def test_ledger_update_and_delete_rejected(self):
        verify_append_only([self.snap],[self.snap,{**self.snap,'hash':'b'}])
        with self.assertRaises(ValueError):verify_append_only([self.snap],[])
        with self.assertRaises(ValueError):verify_append_only([self.snap],[{**self.snap,'generatedAt':'other'}])
if __name__=='__main__':unittest.main()
