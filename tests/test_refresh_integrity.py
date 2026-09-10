"""Independent integrity regressions. Failures identify unremediated review findings."""
import copy
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_data as base
import experiment_model as efficiency
import publication
import record_publication
import refresh
import numpy as np


class RefreshIntegrityTests(unittest.TestCase):
    def test_malformed_download_preserves_last_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'data').mkdir()
            raw=root/'data/games.csv';meta=root/'data/source.json'
            raw.write_bytes(b'last good source');meta.write_text('{"last":"good"}')
            malformed=b'game_id,home_team\n'+b'broken,INVALID\n'*10000
            response=type('Response',(),{'read':lambda self:malformed})()
            with patch.object(refresh,'ROOT',root),patch.dict(refresh.os.environ,{'NFL_OFFLINE':'0'}),patch.object(refresh.urllib.request,'urlopen',return_value=response):
                with self.assertRaises((ValueError,KeyError)):
                    refresh.acquire()
            self.assertEqual(raw.read_bytes(),b'last good source')
            self.assertEqual(meta.read_text(),'{"last":"good"}')

    def test_schedule_rejects_duplicate_matchups_and_partial_scores(self):
        row={'game_id':'g','home_team':'PHI','away_team':'DAL','gameday':'2026-09-10','gametime':'20:00','home_score':None,'away_score':None}
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            refresh.validate_schedule([row,row])
        with self.assertRaisesRegex(ValueError,'Incomplete'):
            refresh.validate_schedule([{**row,'home_score':21}])

    def setUp(self):
        self.game = {'id':'g', 'kickoff':'2026-09-10T20:00:00+00:00', 'status':'final', 'actualHome':24, 'actualAway':21}
        self.snap = {'gameId':'g', 'generatedAt':'2026-09-10T10:00:00+00:00', 'prediction':{'homeWinProbability':.6,'homeMargin':3,'total':45}}
        self.game.update(season=2026,week=1,type='REG',home='PHI',away='DAL',venue='Example stadium',neutral=False)
        self.snap['gameContext']={k:self.game[k] for k in ('season','week','type','home','away','kickoff','venue','neutral')}
        self.snap['hash'] = refresh.digest(self.snap)
        self.receipt = {'status':'ready','publishedAt':'2026-09-10T11:00:00+00:00','snapshotHashes':[self.snap['hash']],'deploymentUrl':'https://example.vercel.app','deploymentId':'dpl_fixture'}

    def test_receipt_does_not_authorize_tampered_snapshot_content(self):
        tampered = copy.deepcopy(self.snap)
        tampered['prediction']['homeWinProbability'] = .99
        self.assertIsNone(publication.eligible_snapshot(self.game,[tampered],[self.receipt]))

    def test_no_forecast_can_publish_exactly_at_kickoff(self):
        self.receipt['publishedAt'] = self.game['kickoff']
        self.assertIsNone(publication.eligible_snapshot(self.game,[self.snap],[self.receipt]))

    def test_ties_are_accounted_without_becoming_decisive_wins(self):
        self.game['actualAway'] = 24
        result = publication.grade_prospective([self.game],[self.snap],[self.receipt])
        self.assertEqual((result['games'],result['ties'],result['missed']), (0,1,0))

    def test_latest_successfully_published_revision_wins(self):
        later = copy.deepcopy(self.snap)
        later['generatedAt'] = '2026-09-10T12:00:00+00:00'
        later['hash'] = refresh.digest({k:v for k,v in later.items() if k!='hash'})
        # Newer local snapshot does not supersede the earlier public one.
        self.assertEqual(publication.eligible_snapshot(self.game,[later,self.snap],[self.receipt]), self.snap)

    def test_invalid_high_score_is_rejected(self):
        with self.assertRaises(ValueError):
            refresh.canonical_prediction(100,102,(14,14),[])

    def test_probability_rounding_never_emits_zero_or_one(self):
        # Both expected scores are within the current score guard.
        try:
            prediction = refresh.canonical_prediction(20,40,(1,14),[])
        except ValueError:
            return  # Rejecting an unsupported degenerate distribution is valid.
        self.assertTrue(0 < prediction['homeWinProbability'] < 1)

    def test_fabricated_ready_evidence_cannot_create_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'data').mkdir(); (root/'scripts').mkdir()
            (root/'data/ledger.json').write_text(json.dumps([self.snap]))
            (root/'data/publications.json').write_text('[]')
            artifact = root/'forged.json'
            artifact.write_text(json.dumps({'games':[{'history':[{'hash':self.snap['hash']}]}]}))
            argv=['record_publication.py','--url','https://example.invalid','--deployment-id','dpl_fake','--artifact',str(artifact)]
            with patch.object(record_publication,'__file__',str(root/'scripts/record_publication.py')), patch.object(sys,'argv',argv):
                try:
                    record_publication.main()
                except (ValueError,SystemExit):
                    pass
            self.assertEqual(json.loads((root/'data/publications.json').read_text()), [])

    def test_offline_digest_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'data').mkdir()
            (root/'data/games.csv').write_text('modified')
            (root/'data/source.json').write_text(json.dumps({'sha256':'wrong'}))
            with patch.object(refresh,'ROOT',root), patch.dict(refresh.os.environ,{'NFL_OFFLINE':'1'}):
                with self.assertRaisesRegex(ValueError,'digest mismatch'):
                    refresh.acquire()


class BlendIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=base.load_rows(base.ROOT/'data/games.csv')
        cls.statmap={}
        for path in (base.ROOT/'data/raw').glob('stats_team_week_*.csv'):
            with path.open(encoding='utf-8-sig') as stream:
                for row in csv.DictReader(stream):
                    cls.statmap[(row['game_id'],base.team(row['team']))]=efficiency.rates(row)
        cls.target=copy.deepcopy(next(r for r in cls.rows if r['game_id']=='2024_01_BAL_KC'))
        cls.original=efficiency.infer_blend(cls.rows,cls.statmap,[cls.target])[cls.target['game_id']]

    def test_same_week_and_future_scores_and_stats_do_not_change_projection(self):
        rows=copy.deepcopy(self.rows); statmap=dict(self.statmap)
        for row in rows:
            if row['gameday']>='2024-09-05':
                row['home_score']=99; row['away_score']=0
                for team in [row['home_team'],row['away_team']]:
                    statmap[(row['game_id'],team)]=np.ones(7)*123
        target=next(r for r in rows if r['game_id']==self.target['game_id'])
        updated=efficiency.infer_blend(rows,statmap,[target])[target['game_id']]
        self.assertEqual(updated['homeMargin'],self.original['homeMargin'])
        self.assertEqual(updated['total'],self.original['total'])

    def test_neutral_game_has_zero_home_field_contribution(self):
        target={**self.target,'location':'Neutral'}
        blend=efficiency.infer_blend(self.rows,self.statmap,[target])[target['game_id']]
        terms=refresh.evidence(blend)
        self.assertAlmostEqual(next(t['points'] for t in terms if t['name']=='Home field'),0,places=3)

if __name__=='__main__':
    unittest.main()
