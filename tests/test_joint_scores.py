import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from joint_scores import reconcile_scores
class JointScoresTests(unittest.TestCase):
    def test_preserves_both_means_ties_support_and_input(self):
        prior=np.ones((41,41));prior[1,:]=0;prior[:,1]=0;original=prior.copy()
        p=reconcile_scores(prior,24.2,20.3,.007)
        h,a=np.indices(p.shape)
        self.assertAlmostEqual(p.sum(),1);self.assertAlmostEqual((p*h).sum(),24.2,places=8);self.assertAlmostEqual((p*a).sum(),20.3,places=8)
        self.assertAlmostEqual(np.trace(p),.007);self.assertTrue((p>=0).all());self.assertTrue(np.isfinite(p).all())
        np.testing.assert_array_equal(prior,original);self.assertEqual(p[1,:].sum()+p[:,1].sum(),0)
    def test_team_swap_symmetry_and_postseason_no_ties(self):
        prior=np.arange(1,962,dtype=float).reshape(31,31)
        p=reconcile_scores(prior,18,22,0)
        q=reconcile_scores(prior.T,22,18,0)
        np.testing.assert_allclose(p.T,q,atol=1e-12);self.assertEqual(np.trace(p),0)
    def test_identity_for_already_satisfied_constraints(self):
        prior=np.array([[.10,.15,.05],[.20,.10,.10],[.05,.10,.15]])
        h,a=np.indices(prior.shape)
        p=reconcile_scores(prior,(prior*h).sum(),(prior*a).sum(),np.trace(prior))
        np.testing.assert_allclose(p,prior,atol=1e-12)
    def test_invalid_infeasible_and_missing_settlement_support_fail(self):
        for prior,h,a,t in [(np.ones((3,3)),4,1,0),(np.ones((3,3)),0,1,0),(np.eye(3),1,1,0),(np.ones((3,3)),1,1,1),(np.array([[1,np.nan],[1,1]]),.5,.5,.1),(np.zeros((3,3)),1,1,.1)]:
            with self.assertRaises(ValueError):reconcile_scores(prior,h,a,t)
    def test_joint_infeasibility_inside_coordinate_bounds(self):
        prior=np.zeros((3,3));prior[0,2]=prior[2,0]=1
        with self.assertRaises(ValueError):reconcile_scores(prior,1.5,1.5,0)
    def test_prior_scale_invariance_and_near_boundary_target(self):
        prior=np.ones((3,3))
        p=reconcile_scores(prior,.001,1.5,0)
        q=reconcile_scores(prior*1e100,.001,1.5,0)
        np.testing.assert_allclose(p,q,atol=1e-9)
        h,a=np.indices(p.shape)
        self.assertAlmostEqual((p*h).sum(),.001,places=8);self.assertAlmostEqual((p*a).sum(),1.5,places=8)
if __name__=='__main__':unittest.main()
