import copy
import hashlib
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from market_benchmark import grade_benchmark, public_summary, digest
from market_pairing import instant


class MarketBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.raw=b'game_id,season,week,game_type,home_team,away_team,gameday,gametime,stadium,location,home_score,away_score\n2026_01_DAL_PHI,2026,1,REG,PHI,DAL,2026-09-13,13:00,Venue,Home,24,20\n'
        game={'id':'2026_01_DAL_PHI','season':2026,'week':1,'type':'REG','home':'PHI','away':'DAL','kickoff':'2026-09-13T17:00:00+00:00','venue':'Venue','neutral':False,'status':'final','actualHome':24,'actualAway':20}
        self.site={'season':2026,'generatedAt':'2026-09-14T12:01:00Z','source':{'sha256':hashlib.sha256(self.raw).hexdigest(),'retrievedAt':'2026-09-14T12:00:00Z'},'games':[game]}
        snapshot={'gameId':game['id'],'gameContext':{k:game[k] for k in ('season','week','type','home','away','kickoff','venue','neutral')},'generatedAt':'2026-09-12T15:00:00Z','prediction':{'homeMargin':3,'total':45}}
        snapshot['hash']=digest(snapshot)
        self.ledger=[snapshot]
        self.receipts=[{'status':'ready','publishedAt':'2026-09-12T16:00:00Z','deploymentUrl':'https://example.vercel.app','snapshotHashes':[snapshot['hash']]}]
        self.captures=[{'sha256':'a'*64,'uploadedAt':'2026-09-13T16:56:00Z','feed':{'fetchedAt':'2026-09-13T16:55:00Z','events':[game|{'books':[{'book':'example','spread':{'homePoint':-2,'observedAt':'2026-09-13T16:54:00Z'},'total':{'point':47,'observedAt':'2026-09-13T16:54:00Z'}}]}]}}]
        self.now=instant('2026-09-14T13:00:00Z')
    def grade(self):
        return grade_benchmark(self.site,self.ledger,self.receipts,self.captures,self.now,self.now,self.raw)
    def test_same_game_errors_have_correct_spread_sign_and_private_trace(self):
        result=self.grade()
        spread,total=result['books']
        self.assertEqual((spread['modelMae'],spread['marketMae']),(1,2))
        self.assertEqual((total['modelMae'],total['marketMae']),(1,3))
        self.assertEqual(result['pairedGameCount'],1)
        self.assertEqual(result['records'][0]['receiptHash'],digest(self.receipts[0]))
        summary=public_summary(result)
        self.assertNotIn('records',summary)
        self.assertNotIn('captureHash',str(summary))
    def test_missing_forecast_never_improves_market_or_model_error(self):
        self.receipts=[]
        result=self.grade()
        self.assertEqual(result['pairedGameCount'],0)
        for book in result['books']:
            self.assertIsNone(book['modelMae'])
            self.assertIsNone(book['marketMae'])
            self.assertEqual(book['exclusionReasons'],{'missing-forecast':1})
    def test_stale_and_post_kickoff_quotes_cannot_enter(self):
        self.captures[0]['feed']['events'][0]['books'][0]['spread']['observedAt']='2026-09-13T16:44:59Z'
        self.assertEqual(self.grade()['books'][0]['exclusionReasons'],{'stale-quote':1})
        self.captures[0]['uploadedAt']='2026-09-13T17:00:00Z'
        self.assertEqual(self.grade()['pairedGameCount'],0)
    def test_absent_market_does_not_remove_other_market(self):
        self.captures[0]['feed']['events'][0]['books'][0]['total']=None
        result=self.grade()
        self.assertEqual(result['books'][0]['pairedGames'],1)
        self.assertEqual(result['books'][1]['exclusionReasons'],{'missing-market':1})
    def test_tied_final_is_included_in_score_errors(self):
        self.raw=self.raw.replace(b',24,20\n',b',20,20\n')
        self.site['source']['sha256']=hashlib.sha256(self.raw).hexdigest()
        self.site['games'][0]['actualHome']=20
        self.assertEqual(self.grade()['books'][0]['modelMae'],3)
    def test_pending_result_is_distinct_from_missing_checkpoint(self):
        self.raw=self.raw.replace(b',24,20\n',b',,\n')
        self.site['source']['sha256']=hashlib.sha256(self.raw).hexdigest()
        self.site['games'][0].update(status='scheduled',actualHome=None,actualAway=None)
        result=self.grade()
        self.assertEqual(result['books'][0]['exclusionReasons'],{'pending-result':1})
        self.captures=[]
        result=self.grade()
        self.assertEqual(result['records'][0]['status'],'missing-book-coverage')
        self.assertEqual(result['records'][0]['resultStatus'],'pending-result')
    def test_source_mismatch_and_backdated_final_fail_closed(self):
        self.site['games'][0]['actualHome']=30
        with self.assertRaisesRegex(ValueError,'differs'):self.grade()
        self.site['games'][0]['actualHome']=24
        self.site['source']['retrievedAt']='2026-09-13T16:59:00Z'
        with self.assertRaisesRegex(ValueError,'post-kickoff'):self.grade()
    def test_future_generated_edition_cannot_enter_benchmark(self):
        self.site['generatedAt']='2199-01-01T00:00:00Z'
        with self.assertRaisesRegex(ValueError,'chronology'):self.grade()
    def test_books_are_separate_and_latest_forecast_after_entry_is_not_selected(self):
        later=copy.deepcopy(self.ledger[0]);later['generatedAt']='2026-09-13T16:00:00Z';later['prediction']['homeMargin']=4;later.pop('hash');later['hash']=digest(later)
        self.ledger.append(later)
        self.receipts.append(self.receipts[0]|{'publishedAt':'2026-09-13T16:30:00Z','snapshotHashes':[later['hash']]})
        book=copy.deepcopy(self.captures[0]['feed']['events'][0]['books'][0]);book['book']='other';book['spread']['homePoint']=-4
        self.captures[0]['feed']['events'][0]['books'].append(book)
        result=self.grade()
        self.assertEqual(len(result['books']),4)
        self.assertEqual(result['books'][0]['modelMae'],1)
        self.assertEqual(result['books'][2]['marketMae'],0)


if __name__=='__main__':unittest.main()
