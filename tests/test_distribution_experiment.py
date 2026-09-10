import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import experiment_distribution as d

class DistributionTests(unittest.TestCase):
    def test_probability_and_swap_symmetry(self):
        residuals=np.random.default_rng(9).normal(4,12,500)
        for method in d.METHODS:
            a=d.distribution(4.35,residuals,method);b=d.distribution(-4.35,residuals,method)
            self.assertAlmostEqual(a.sum(),1);self.assertTrue((a>=0).all())
            np.testing.assert_allclose(a,b[::-1],atol=1e-14)
            self.assertGreater(a[100],0)

    def test_zero_mean_three_way_probabilities(self):
        for method in d.METHODS:
            pmf=d.distribution(0,np.linspace(-20,20,200),method)
            self.assertAlmostEqual(pmf[:100].sum(),pmf[101:].sum())
            self.assertAlmostEqual(pmf[:100].sum()+pmf[100]+pmf[101:].sum(),1)

    def test_proper_scores_reward_correct_point_mass(self):
        mass=np.zeros(201);mass[103]=1
        right=d.measure(mass,3);wrong=d.measure(mass,7)
        self.assertEqual(right['logScore'],0);self.assertEqual(right['crps'],0)
        self.assertGreater(wrong['logScore'],right['logScore']);self.assertEqual(wrong['crps'],4)

    def test_future_residual_cannot_change_target_distribution_scores(self):
        records=[]
        for i in range(100):records.append({'row':{'gameday':'2020-12-01','season':2020,'home_score':i%30,'away_score':10},'margin':2.,'cutoff':'2020-11-26'})
        records.append({'row':{'game_id':'target','gameday':'2021-09-12','season':2021,'home_score':20,'away_score':17},'margin':2.,'cutoff':'2021-09-09'})
        future={'row':{'game_id':'future','gameday':'2021-09-19','season':2021,'home_score':100,'away_score':0},'margin':2.,'cutoff':'2021-09-16'}
        for method in d.METHODS:
            for preserving in [False,True]:
                self.assertEqual(d.evaluate(records,method,mean_preserving=preserving)[0],d.evaluate(records+[future],method,mean_preserving=preserving)[0])

    def test_postseason_tie_exactly_zero_and_normalization(self):
        mass=d.distribution(3,np.linspace(-20,20,200),'empirical_bw2')
        tied=d.settlement_constrain(mass,d.prior_tie_probability([], '2023-01-20','POST'))
        self.assertEqual(tied[100],0);self.assertAlmostEqual(tied.sum(),1)
        self.assertTrue((tied>=0).all())
        for probability in [0,.01,.05]:
            a=d.settlement_constrain(mass,probability)
            b=d.settlement_constrain(mass[::-1],probability)
            np.testing.assert_allclose(a,b[::-1],atol=1e-14)

    def test_tie_rate_excludes_cutoff_future_and_postseason(self):
        row=lambda date,kind,h,a:{'row':{'gameday':date,'game_type':kind,'home_score':h,'away_score':a}}
        eligible=[row('2022-09-01','REG',7,7),row('2022-09-02','REG',14,7)]
        extra=[row('2022-09-08','REG',7,7),row('2022-09-09','REG',7,7),row('2022-09-01','POST',7,7),row('2022-09-01','REG',None,None)]
        p=d.prior_tie_probability(eligible,'2022-09-08','REG')
        self.assertAlmostEqual(p,2/102)
        self.assertEqual(p,d.prior_tie_probability(eligible+extra,'2022-09-08','REG'))
        self.assertEqual(d.prior_tie_probability([], '2022-09-08','REG'),.01)

    def test_constrained_mean_and_swap_symmetry(self):
        residuals=np.linspace(-20,20,200)
        for mean in [-30.,-3.2,0.,3.2,30.]:
            for tie in [0.,.01,.1]:
                original=d.distribution(mean,residuals,'empirical_bw2')
                saved=original.copy()
                pmf=d.constrain_mean(original,tie,mean)
                self.assertAlmostEqual(float(pmf@d.GRID),mean,places=9)
                self.assertEqual(pmf[100],tie)
                self.assertAlmostEqual(float(pmf.sum()),1.,places=12)
                self.assertTrue(np.all(pmf>=0))
                np.testing.assert_array_equal(original,saved)
                np.testing.assert_allclose(pmf,d.constrain_mean(original[::-1],tie,-mean)[::-1],atol=1e-12)

    def test_mean_constraint_preserves_support_and_rejects_infeasible_input(self):
        mass=np.zeros(201);mass[98]=.25;mass[100]=.5;mass[104]=.25
        pmf=d.constrain_mean(mass,.2,1.6)
        self.assertAlmostEqual(pmf[98],.8/3)
        self.assertAlmostEqual(pmf[104],1.6/3)
        self.assertTrue(np.all(pmf[mass==0]==0))
        for mean in [-2.,4.,float('nan')]:
            with self.assertRaises(ValueError):d.constrain_mean(mass,.2,mean)
        for bad in [np.zeros(201),np.ones(200),np.full(201,np.nan),-np.ones(201)]:
            with self.assertRaises(ValueError):d.constrain_mean(bad,.01,0.)
        for tie in [-.1,1.,float('nan')]:
            with self.assertRaises(ValueError):d.constrain_mean(mass,tie,0.)

    def test_mean_constraint_identity_and_near_boundary_stability(self):
        original=np.zeros(201);original[98]=.3;original[100]=.1;original[104]=.6
        np.testing.assert_allclose(d.constrain_mean(original,.1,float(original@d.GRID)),original,atol=1e-14)
        for conditional in [-2.+1e-8,4.-1e-8]:
            mean=.9*conditional
            result=d.constrain_mean(original,.1,mean)
            self.assertTrue(np.isfinite(result).all())
            self.assertAlmostEqual(float(result@d.GRID),mean,places=10)
        degenerate=np.zeros(201);degenerate[104]=1.
        with self.assertRaises(ValueError):d.constrain_mean(degenerate,.1,3.6)

    def test_math_erf_cdf_reference_values(self):
        np.testing.assert_allclose(d.ndtr(np.array([0.,1.,-1.])),[.5,.8413447460685429,.15865525393145707],atol=1e-15)

if __name__=='__main__':unittest.main()
