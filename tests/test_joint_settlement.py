import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_joint_settlement import settlement,paired_losses

class JointSettlementTests(unittest.TestCase):
    def test_no_lines_means_unknown_comparison(self):
        self.assertTrue(all(v is None for v in paired_losses([],'brier').values()))
    def test_signed_line_and_side_swap(self):
        m=np.zeros((31,31));m[24,21]=.5;m[21,24]=.2;m[30,20]=.3
        r=settlement(m,3,3,'spread')
        np.testing.assert_allclose(r['probabilities'],[.3,.5,.2])
        self.assertEqual(r['outcome'],1)
        self.assertAlmostEqual(r['brier'],.38)
        self.assertAlmostEqual(r['logLoss'],-np.log(.5))
        swap=settlement(m.T,-3,-3,'spread')
        np.testing.assert_allclose(swap['probabilities'],[.2,.5,.3])
        self.assertAlmostEqual(swap['brier'],r['brier'])

    def test_half_points_cannot_push_and_total_uses_sum(self):
        m=np.zeros((31,31));m[24,21]=.7;m[30,20]=.3
        self.assertEqual(settlement(m,3.5,3,'spread')['outcome'],2)
        self.assertEqual(settlement(m,3.5,3,'spread')['probabilities'][1],0)
        r=settlement(m,45,45,'total')
        np.testing.assert_allclose(r['probabilities'],[.3,.7,0])
        self.assertEqual(r['outcome'],1)
        self.assertEqual(settlement(m,44.5,45,'total')['probabilities'],[1,0,0])

    def test_invalid_or_impossible_outcomes_fail(self):
        m=np.zeros((4,4));m[3,0]=1
        for line in [None,True,.25,np.nan,np.inf]:
            with self.assertRaises(ValueError):settlement(m,line,3,'spread')
        for actual in [4,-4,.5,np.nan]:
            with self.assertRaises(ValueError):settlement(m,3,actual,'spread')
        with self.assertRaisesRegex(ValueError,'Zero probability'):settlement(m,3,0,'spread')
        with self.assertRaises(ValueError):settlement(m*2,3,3,'spread')
if __name__=='__main__':unittest.main()
