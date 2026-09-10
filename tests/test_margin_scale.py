import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from experiment_margin_scale import fit_scale,experiment
class MarginScaleTests(unittest.TestCase):
    def rows(self):return [dict(id=str(i),season=2024 if i<2 else 2025,week=i+1,homeMargin=(-2 if i%2 else 2),actualMargin=(-4 if i%2 else 4)) for i in range(4)]
    def test_known_scale_and_side_swap_symmetry(self):
        rows=self.rows();self.assertEqual(fit_scale(rows[:2]),2)
        swapped=[{**r,'homeMargin':-r['homeMargin'],'actualMargin':-r['actualMargin']} for r in rows]
        self.assertEqual(fit_scale(swapped[:2]),2)
        result=experiment(rows);self.assertEqual(result['evaluation']['candidateMae'],0)
        self.assertEqual(result['evaluation']['difference'],-2)
    def test_later_outcome_poisoning_cannot_change_fitted_scale(self):
        rows=self.rows();before=experiment(rows)
        rows[-1]['actualMargin']=1000
        after=experiment(rows)
        self.assertEqual(before['alpha'],after['alpha'])
        self.assertNotEqual(before['evaluation']['candidateMae'],after['evaluation']['candidateMae'])
    def test_degenerate_invalid_and_negative_fit(self):
        for rows in [[],[{'homeMargin':0,'actualMargin':1}],[{'homeMargin':float('nan'),'actualMargin':1}]]:
            with self.assertRaises(ValueError):fit_scale(rows)
        self.assertEqual(fit_scale([{'homeMargin':1,'actualMargin':-1}]),0)
if __name__=='__main__':unittest.main()
