import copy, hashlib, json, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_data as engine
import numpy as np

class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=engine.load_rows(engine.ROOT/'data/games.csv')
        cls.game=next(r for r in cls.rows if r['game_id']=='2024_01_BAL_KC')
        cls.beta,_,_=engine.fit(cls.rows,'2024-09-05',180,20)
    def test_future_results_cannot_change_prediction(self):
        changed=copy.deepcopy(self.rows)
        for r in changed:
            if r['gameday']>='2024-09-05':r['home_score']=99;r['away_score']=0
        beta,_,last=engine.fit(changed,'2024-09-05',180,20)
        np.testing.assert_array_equal(self.beta,beta)
        self.assertLess(last,'2024-09-05')
    def test_market_is_not_an_input(self):
        game=copy.deepcopy(self.game);original=engine.predict(self.beta,game)
        game['spread_line']='99';game['total_line']='150';game['home_moneyline']='-9999'
        self.assertEqual(original,engine.predict(self.beta,game))
    def test_components_and_scores_reconcile(self):
        p=engine.predict(self.beta,self.game)
        self.assertAlmostEqual(sum(c['points'] for c in p['contributions']),p['homeMargin'],places=2)
        self.assertAlmostEqual(p['homeScore']-p['awayScore'],p['homeMargin'],places=1)
        self.assertAlmostEqual(p['homeScore']+p['awayScore'],p['total'],places=1)
        self.assertTrue(0<p['homeWinProbability']<1)
    def test_neutral_field_is_zero(self):
        game={**self.game,'location':'Neutral'};p=engine.predict(self.beta,game)
        self.assertEqual(p['contributions'][-1]['points'],0)
    def test_ledger_hash_and_kickoff(self):
        rows={r['game_id']:r for r in self.rows}
        for snapshot in json.loads((engine.ROOT/'data/ledger.json').read_text()):
            payload={k:v for k,v in snapshot.items() if k!='hash'}
            self.assertEqual(hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest(),snapshot['hash'])
            self.assertLess(engine.datetime.fromisoformat(snapshot.get('generatedAt',snapshot.get('publishedAt'))),engine.kickoff(rows[snapshot['gameId']]))
    def test_replay_accounting(self):
        data=json.loads((engine.ROOT/'data/site.json').read_text());m=data['performance']['aggregate']
        self.assertEqual(m['decisiveGames']+m['ties'],m['games'])
        for key in ['ats','totals']:self.assertEqual(sum(m[key].values()),m['games'])
        self.assertEqual(sum(b['count'] for b in m['calibration']),m['decisiveGames'])
        for p in data['performance']['records']:
            game=next(r for r in self.rows if r['game_id']==p['id'])
            self.assertLess(p['trainingThrough'],game['gameday'])
if __name__=='__main__':unittest.main()
