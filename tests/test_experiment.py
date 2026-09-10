"""Independent perturbation tests of the experimental feature/inference boundary."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import experiment_model as e
import build_data as b

class ExperimentLeakage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=[r for r in b.load_rows(e.ROOT/'data/games.csv') if r['home_score'] is not None and r['away_score'] is not None and r['season']<=2025]
        downloads=[e.download(s) for s in range(2010,2026)]
        cls.sm={(r['game_id'],b.team(r['team'])):e.rates(r) for records,_ in downloads for r in records}
        cls.targets=[r for r in cls.rows if r['season']==2024 and r['week']==1]

    def test_target_and_future_stats_cannot_change_target_features(self):
        x,rr=e.features(self.rows,self.sm,90)
        future={r['game_id'] for r in self.rows if r['season']>=2024}
        altered={k:v+999 if k[0] in future else v for k,v in self.sm.items()}
        xx,_=e.features(self.rows,altered,90)
        ix=[i for i,r in enumerate(rr) if r['season']<2024 or (r['season']==2024 and r['week']==1)]
        np.testing.assert_array_equal(x[ix],xx[ix])

    def test_future_scores_cannot_change_current_inference(self):
        a=e.infer_epa(self.rows,self.sm,self.targets)
        altered=[dict(r,home_score=99,away_score=0) if r['season']>=2024 else r for r in self.rows]
        targets=[r for r in altered if r['season']==2024 and r['week']==1]
        z=e.infer_epa(altered,self.sm,targets)
        for key in a:
            self.assertEqual(a[key]['homeMargin'],z[key]['homeMargin'])
            self.assertEqual(a[key]['total'],z[key]['total'])
            self.assertAlmostEqual(sum(c['points'] for c in a[key]['contributions']),a[key]['homeMargin'])

    def test_complete_join_and_finite_features(self):
        keys={(r['game_id'],t) for r in self.rows if r['season']>=2010 for t in [r['home_team'],r['away_team']]}
        self.assertFalse(keys-set(self.sm))
        x,_=e.features(self.rows,self.sm,90)
        self.assertTrue(np.isfinite(x).all())

    def test_neutral_swap_symmetry_end_to_end(self):
        target=dict(self.targets[0],location='Neutral')
        swapped=dict(target,home_team=target['away_team'],away_team=target['home_team'])
        a=e.infer_epa(self.rows,self.sm,[target])[target['game_id']]
        b=e.infer_epa(self.rows,self.sm,[swapped])[target['game_id']]
        self.assertAlmostEqual(a['homeMargin'],-b['homeMargin'],places=12)
        self.assertAlmostEqual(a['total'],b['total'],places=12)
        self.assertAlmostEqual(a['homeScore'],b['awayScore'],places=12)
        self.assertAlmostEqual(sum(c['points'] for c in a['contributions']),a['homeMargin'],places=12)
        self.assertEqual(a['contributions'][0]['points'],0)
        self.assertEqual(a['contributions'][1]['points'],0)
        blend=e.infer_blend(self.rows,self.sm,[target])[target['game_id']]
        other=e.infer_blend(self.rows,self.sm,[swapped])[target['game_id']]
        self.assertAlmostEqual(blend['homeMargin'],-other['homeMargin'],places=12)
        self.assertAlmostEqual(blend['total'],other['total'],places=12)
        self.assertAlmostEqual(sum(c['points'] for c in blend['contributions']),blend['homeMargin'],places=12)

    def test_structural_exclusion_survives_biased_training(self):
        rng=np.random.default_rng(19)
        x=rng.normal(3,2,(100,30));x[:,0]=1;x[:,1]=rng.integers(0,2,100)
        y=rng.normal(10,5,(100,2))
        beta=e.fit_symmetric(x,y,10)
        self.assertTrue(np.array_equal(beta[np.r_[0,np.arange(16,30)],0],np.zeros(15)))
        self.assertTrue(np.array_equal(beta[2:16,1],np.zeros(14)))
        probe=x[:10].copy();probe[:,1]=0
        swap=probe.copy();swap[:,2:16]*=-1
        np.testing.assert_allclose((probe@beta)[:,0],-(swap@beta)[:,0],atol=1e-12)
        np.testing.assert_allclose((probe@beta)[:,1],(swap@beta)[:,1],atol=1e-12)

if __name__=='__main__':unittest.main()
