import gzip
import hashlib
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from market_capture import decode_capture
from market_pairing import pair_checkpoint


class MarketCaptureTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,9,12,12,tzinfo=timezone.utc)
        self.feed={'state':'ready','fetchedAt':'2026-09-12T11:59:00.000Z','events':[]}
    def encode(self):
        body=json.dumps({'schemaVersion':1,'provider':'The Odds API','feed':self.feed}).encode()
        compressed=gzip.compress(body); digest=hashlib.sha256(body).hexdigest()
        return compressed, {'pathname':'odds/2026-09-12/2026-09-12T11-59-00.000Z-'+digest+'.json.gz','compressedHash':hashlib.sha256(compressed).hexdigest(),'uploadedAt':'2026-09-12T11:59:01Z'}
    def test_verified_archive_and_corruption(self):
        body,meta=self.encode()
        self.assertEqual(decode_capture(body,meta,self.now)['feed'],self.feed)
        for change in [{'compressedHash':'0'*64},{'pathname':meta['pathname'].replace('11-59','11-58')},{'uploadedAt':'2026-09-12T11:58:00Z'},{'uploadedAt':'2026-09-12T12:01:00Z'}]:
            with self.assertRaises(ValueError):decode_capture(body,meta|change,self.now)
    def test_invalid_prices_rejected_even_with_valid_hashes(self):
        self.feed['events']=[{'id':'e','home':'PHI','away':'DAL','kickoff':'2026-09-13T12:00:00Z','books':[{'book':'example','spread':{'observedAt':self.feed['fetchedAt'],'homePrice':True,'awayPrice':-110,'homePoint':-3}}]}]
        body,meta=self.encode()
        with self.assertRaises(ValueError):decode_capture(body,meta,self.now)
    def test_wrapper_enforces_pending_and_strict_closing_cutoff(self):
        game={'id':'g','home':'PHI','away':'DAL','kickoff':'2026-09-12T12:00:00Z'}
        self.assertEqual(pair_checkpoint(game,'entry',self.now,[],[],[],'example','spread')['status'],'incomplete')
        future=game|{'kickoff':'2026-09-14T12:00:00Z'}
        self.assertEqual(pair_checkpoint(future,'entry',self.now,[],[],[],'example','spread')['status'],'pending')
        capture={'sha256':'a'*64,'uploadedAt':game['kickoff'],'feed':{'fetchedAt':'2026-09-12T11:59:00Z','events':[game|{'books':[]}]}}
        self.assertEqual(pair_checkpoint(game,'closing',self.now,[],[],[capture],'example','spread')['status'],'missing-capture')
