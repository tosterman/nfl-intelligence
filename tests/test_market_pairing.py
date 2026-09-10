import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from market_pairing import checkpoint, quote_at, forecast_at
from refresh import digest


class MarketPairingTests(unittest.TestCase):
    def setUp(self):
        self.cutoff=datetime(2026,9,12,12,tzinfo=timezone.utc)
        self.game={'home':'PHI','away':'DAL','kickoff':'2026-09-13T12:00:00Z'}
        self.quote={'observedAt':'2026-09-12T11:59:00Z','homePrice':-110,'awayPrice':-110,'homePoint':-3}
        self.capture={'sha256':'a'*64,'uploadedAt':'2026-09-12T11:59:02Z','feed':{'fetchedAt':'2026-09-12T11:59:01Z','events':[self.game | {'books':[{'book':'example','spread':self.quote}]}]}}
    def select(self,captures,**kwargs):
        return quote_at(self.game,captures,'example','spread',self.cutoff,timedelta(hours=6),**kwargs)
    def test_pending_and_pre_protocol_are_not_missing_quotes(self):
        self.assertEqual(checkpoint(self.game,'entry',self.cutoff-timedelta(seconds=1))['status'],'pending')
        self.assertEqual(checkpoint(self.game | {'kickoff':'2026-09-11T12:00:00Z'},'entry',self.cutoff)['status'],'excluded-before-protocol')
    def test_future_upload_cannot_backfill_checkpoint(self):
        self.assertEqual(self.select([self.capture])['status'],'matched')
        self.assertEqual(self.select([self.capture | {'uploadedAt':'2026-09-12T12:00:01Z'}])['status'],'missing-capture')
    def test_latest_missing_book_does_not_reuse_older_price(self):
        newer=self.capture | {'sha256':'b'*64,'uploadedAt':'2026-09-12T12:00:00Z','feed':{'fetchedAt':'2026-09-12T11:59:59Z','events':[self.game | {'books':[]}]}}
        self.assertEqual(self.select([self.capture,newer])['status'],'missing-book')
    def test_same_time_conflict_rejected(self):
        with self.assertRaises(ValueError):self.select([self.capture,self.capture | {'sha256':'b'*64}])
    def test_kickoff_boundary_and_stale_update(self):
        at=self.capture | {'uploadedAt':self.cutoff.isoformat()}
        self.assertEqual(self.select([at],exclusive=True)['status'],'missing-capture')
        self.quote['observedAt']='2026-09-12T05:59:59Z'
        self.assertEqual(self.select([self.capture])['status'],'stale-quote')
    def test_different_matchup_does_not_match(self):
        self.game=self.game | {'kickoff':'2026-09-13T13:00:00Z'}
        self.assertEqual(self.select([self.capture])['status'],'missing-capture')

    def test_forecast_requires_hash_context_and_checkpoint_publication(self):
        game=self.game | {'id':'g','season':2026,'week':1,'type':'REG','venue':'Example','neutral':False}
        snapshot={'gameId':'g','gameContext':{k:v for k,v in game.items() if k!='id'},'generatedAt':'2026-09-12T11:00:00Z','prediction':{'homeMargin':3}}
        snapshot['hash']=digest(snapshot)
        receipt={'status':'ready','publishedAt':'2026-09-12T11:30:00Z','deploymentUrl':'https://example.vercel.app','snapshotHashes':[snapshot['hash']]}
        self.assertEqual(forecast_at(game,[snapshot],[receipt],self.cutoff)['status'],'matched')
        self.assertEqual(forecast_at(game,[snapshot],[receipt | {'publishedAt':'2026-09-12T12:00:01Z'}],self.cutoff)['status'],'missing-forecast')
        self.assertEqual(forecast_at(game,[snapshot | {'prediction':{'homeMargin':10}}],[receipt],self.cutoff)['status'],'missing-forecast')
        self.assertEqual(forecast_at(game | {'venue':'Other'},[snapshot],[receipt],self.cutoff)['status'],'missing-forecast')
    def test_forecast_timestamp_ties_are_input_order_independent(self):
        game=self.game|{'id':'g','season':2026,'week':1,'type':'REG','venue':'Example','neutral':False}
        a={'gameId':'g','gameContext':{k:v for k,v in game.items() if k!='id'},'generatedAt':'2026-09-12T11:00:00Z','prediction':{'homeMargin':3}}
        a['hash']=digest(a)
        b={k:v for k,v in a.items() if k!='hash'}; b['prediction']={'homeMargin':4}; b['hash']=digest(b)
        receipt={'status':'ready','publishedAt':'2026-09-12T11:30:00Z','deploymentUrl':'https://example.vercel.app','snapshotHashes':[a['hash'],b['hash']]}
        expected=max(a['hash'],b['hash'])
        for ledger in [[a,b],[b,a]]:
            self.assertEqual(forecast_at(game,ledger,[receipt],self.cutoff)['snapshot']['hash'],expected)
