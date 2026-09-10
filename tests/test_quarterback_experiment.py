import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from experiment_quarterback import difference,fit_adjustment,paired_weeks
class QuarterbackExperimentTests(unittest.TestCase):
    def test_swap_symmetry_and_unknown_fallback(self):
        h={'status':'available','netYardsPerDropback':7,'sackRate':.05};a={'status':'available','netYardsPerDropback':5,'sackRate':.1}
        self.assertEqual(difference(h,h),[0,0])
        np.testing.assert_allclose(difference(h,a),-np.array(difference(a,h)))
        self.assertIsNone(difference(h,a|{'status':'unavailable'}))
    def test_fixed_ridge_no_intercept(self):
        x=np.array([[1.,0.],[0.,1.]])
        np.testing.assert_allclose(fit_adjustment(x,np.array([22.,-11.])),[2.,-1.])
        np.testing.assert_allclose(fit_adjustment(np.zeros((2,2)),np.array([100.,-5.])),[0,0])
    def test_week_clusters_weight_games_and_preserve_pairs(self):
        rows=[{'week':w,'actualMargin':0,'baselineMargin':3,'candidateMargin':1} for w in [1,1,1,2]]
        result=paired_weeks(rows,100)
        self.assertEqual(result['clusters'],2)
        self.assertEqual(result['maeDelta'],-2)
        self.assertEqual(result['percentile95'],[-2,-2])
        for row in rows:row['candidateMargin']=row['baselineMargin']
        self.assertEqual(paired_weeks(rows,100)['percentile95'],[0,0])
if __name__=='__main__':unittest.main()
