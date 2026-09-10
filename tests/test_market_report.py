import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from report_market_pairing import build_report, verify_protocol


class MarketReportTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,9,12,12,tzinfo=timezone.utc)
        self.game={'id':'g','home':'PHI','away':'DAL','kickoff':'2026-09-13T12:00:00Z'}
    def test_complete_checkpoint_coverage_without_quotes(self):
        r=build_report([self.game],[],[],[],self.now,self.now)
        self.assertEqual(len(r['checkpoints']),2)
        self.assertEqual(r['checkpointCounts'],{'missing-book-coverage':1,'pending':1})
        self.assertEqual(r['checkpoints'][0]['forecast']['status'],'missing-forecast')
    def test_future_books_do_not_define_past_coverage(self):
        capture={'uploadedAt':'2026-09-12T12:00:02Z','feed':{'fetchedAt':'2026-09-12T12:00:01Z','events':[self.game|{'books':[{'book':'future'}]}]}}
        r=build_report([self.game],[],[],[capture],self.now,self.now)
        self.assertEqual(r['checkpoints'][0]['markets'],[])
    def test_missing_kickoff_and_duplicate_game(self):
        r=build_report([self.game|{'kickoff':None}],[],[],[],self.now,self.now)
        self.assertEqual(r['checkpointCounts'],{'missing-kickoff':2})
        with self.assertRaises(ValueError):build_report([self.game,self.game],[],[],[],self.now,self.now)
    def test_changed_protocol_rejected(self):
        import json
        root=Path(__file__).resolve().parents[1]
        receipt=json.loads((root/'reviews/market-pairing-protocol-publication.json').read_text())
        body=(root/'reviews/market-pairing-protocol.md').read_bytes()
        verify_protocol(body,receipt,self.now)
        with self.assertRaises(ValueError):verify_protocol(body+b'changed',receipt,self.now)
    def test_due_checkpoint_retains_each_market_and_missing_status(self):
        from refresh import digest
        game=self.game|{'season':2026,'week':1,'type':'REG','venue':'Example','neutral':False}
        snap={'gameId':'g','gameContext':{k:v for k,v in game.items() if k!='id'},'generatedAt':'2026-09-12T10:00:00Z','prediction':{'homeMargin':3}}
        snap['hash']=digest(snap)
        receipt={'status':'ready','publishedAt':'2026-09-12T10:01:00Z','snapshotHashes':[snap['hash']],'deploymentUrl':'https://example.vercel.app'}
        quote={'observedAt':'2026-09-12T11:59:00Z','homePrice':-110,'awayPrice':-110,'homePoint':-3}
        capture={'sha256':'a'*64,'uploadedAt':'2026-09-12T11:59:02Z','feed':{'fetchedAt':'2026-09-12T11:59:01Z','events':[game|{'books':[{'book':'example','spread':quote}]}]}}
        r=build_report([game],[snap],[receipt],[capture],self.now,self.now)
        markets=r['checkpoints'][0]['markets']
        self.assertEqual([m['market'] for m in markets],['spread','total','moneyline'])
        self.assertEqual([m['status'] for m in markets],['matched','incomplete','incomplete'])
        self.assertEqual(markets[1]['quote']['status'],'missing-market')
        self.assertEqual(markets[0]['forecast']['snapshot']['hash'],snap['hash'])

    def test_old_export_leaves_due_checkpoint_unassessed(self):
        from datetime import timedelta
        cutoff=self.now-timedelta(seconds=1)
        r=build_report([self.game],[],[],[],self.now,cutoff)
        self.assertEqual(r['checkpointCounts'],{'export-too-early':1,'pending':1})
        self.assertEqual(r['checkpoints'][0]['markets'],[])
        self.assertNotIn('forecast',r['checkpoints'][0])
        self.assertEqual(r['coverageThrough'],cutoff.isoformat())
    def test_future_export_coverage_rejected(self):
        from datetime import timedelta
        with self.assertRaises(ValueError):
            build_report([self.game],[],[],[],self.now,self.now+timedelta(seconds=1))
