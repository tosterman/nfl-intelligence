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
        for status,at in [('failed','2026-09-10T11:00:00+00:00'),('ready','2026-09-10T21:00:00+00:00'),('ready','2026-09-10T20:00:00+00:00'),('ready','2026-09-10T09:00:00+00:00')]:
            self.assertIsNone(eligible_snapshot(self.game,[self.snap],[{'status':status,'publishedAt':at,'snapshotHashes':[self.snap['hash']],'deploymentUrl':'https://example.vercel.app'}]))
    def test_valid_receipt_scores_original_prediction(self):
        receipts=[{'status':'ready','publishedAt':'2026-09-10T11:00:00+00:00','snapshotHashes':[self.snap['hash']],'deploymentUrl':'https://example.vercel.app'}]
        result=grade_prospective([self.game],[self.snap],receipts)
        self.assertEqual(result['games'],1);self.assertEqual(result['wins'],1);self.assertAlmostEqual(result['brier'],.16)
    def test_ledger_update_and_delete_rejected(self):
        verify_append_only([self.snap],[self.snap,{**self.snap,'hash':'b'}])
        with self.assertRaises(ValueError):verify_append_only([self.snap],[])
        with self.assertRaises(ValueError):verify_append_only([self.snap],[{**self.snap,'generatedAt':'other'}])
    def test_ties_keep_score_errors_but_not_conditional_probability_scores(self):
        game={**self.game,'actualHome':20,'actualAway':20}
        receipts=[{'status':'ready','publishedAt':'2026-09-10T11:00:00+00:00','snapshotHashes':[self.snap['hash']],'deploymentUrl':'https://example.vercel.app'}]
        result=grade_prospective([game],[self.snap],receipts)
        self.assertEqual((result['games'],result['ties'],result['scoreGames']),(0,1,1))
        self.assertIsNone(result['brier']);self.assertIsNone(result['logLoss'])
        self.assertEqual(result['marginMae'],3);self.assertEqual(result['totalMae'],5)
        self.assertEqual(result['scoreRecords'][0]['snapshotHash'],self.snap['hash'])
        self.assertEqual(result['calibration'],[])
    def test_last_eligible_forecast_and_interval_boundaries(self):
        newer={**self.snap,'generatedAt':'2026-09-10T12:00:00+00:00','prediction':{'homeWinProbability':.75,'homeMargin':1,'total':48,'marginInterval80':[3,10],'totalInterval80':[40,45]}}
        newer['hash']=digest({k:v for k,v in newer.items() if k!='hash'})
        receipts=[{'status':'ready','publishedAt':'2026-09-10T13:00:00+00:00','snapshotHashes':[self.snap['hash'],newer['hash']],'deploymentUrl':'https://example.vercel.app'}]
        result=grade_prospective([self.game],[newer,self.snap],receipts)
        self.assertEqual(result['scoreRecords'][0]['snapshotHash'],newer['hash'])
        self.assertEqual(result['marginMae'],2);self.assertEqual(result['totalMae'],3)
        self.assertEqual(result['marginIntervalCoverage'],1);self.assertEqual(result['totalIntervalCoverage'],1)
        self.assertAlmostEqual(result['logLoss'],0.2876820724517809)
        self.assertEqual(result['calibration'][0]['count'],1)
        self.assertEqual(result['calibration'][0]['predicted'],.75)
        self.assertEqual(result['calibration'][0]['observed'],1)
        empty=grade_prospective([self.game],[self.snap],[])
        self.assertEqual(empty['scoreGames'],0);self.assertIsNone(empty['marginMae']);self.assertEqual(empty['missed'],1)
        self.assertEqual(empty['calibration'],[])
if __name__=='__main__':unittest.main()
