import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from evaluate_joint_scores import priors,score
class JointEvaluationTests(unittest.TestCase):
    def test_point_mass_scores_are_zero_and_impossible_outcome_rejected(self):
        p=np.zeros((4,4));p[3,1]=1
        result=score(p,3,1)
        for key,value in result.items():self.assertEqual(value,0)
        with self.assertRaises(ValueError):score(p,1,3)
    def test_known_two_outcome_scores(self):
        p=np.zeros((3,3));p[2,0]=p[0,2]=.5
        result=score(p,2,0)
        self.assertAlmostEqual(result['jointLogScore'],np.log(2));self.assertAlmostEqual(result['marginCrps'],1)
        self.assertEqual(result['totalCrps'],0);self.assertEqual(result['threeOutcomeBrier'],.5)
    def test_future_outcomes_cannot_change_frozen_prior(self):
        rows=[dict(season=2023,home_score=h,away_score=a,game_type='REG') for h,a in [(7,0),(3,10),(14,14),(21,3)]]
        p,q,fit=priors(rows)
        future=rows+[dict(season=2025,home_score=99,away_score=98,game_type='REG')]
        p2,q2,fit2=priors(future)
        np.testing.assert_array_equal(p,p2);np.testing.assert_array_equal(q,q2);self.assertEqual(fit,fit2)
        np.testing.assert_allclose(p,p.T);np.testing.assert_allclose(q,q.T)
if __name__=='__main__':unittest.main()
