import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from calibration import calibration_bins

class LiveCalibrationTests(unittest.TestCase):
    def test_fixed_boundaries_partition_all_decisive_results(self):
        rows=[{'probability':p,'outcome':i%2} for i,p in enumerate([0,.39999,.4,.5,.6,.7,1])]
        bins=calibration_bins(rows)
        self.assertEqual([b['count'] for b in bins],[2,1,1,1,2])
        self.assertEqual(sum(b['count'] for b in bins),7)
        self.assertEqual(bins[-1]['predicted'],.85)
    def test_single_result_uncertainty_and_empty_sample(self):
        self.assertEqual(calibration_bins([]),[])
        win=calibration_bins([{'probability':.6,'outcome':1}])[0]
        self.assertEqual(win['observed'],1)
        self.assertAlmostEqual(win['observedLow95'],.2065432915)
        self.assertAlmostEqual(win['observedHigh95'],1)
        loss=calibration_bins([{'probability':.6,'outcome':0}])[0]
        self.assertAlmostEqual(loss['observedHigh95'],.7934567085)
    def test_invalid_inputs_fail_instead_of_disappearing_from_bins(self):
        for row in [{'probability':float('nan'),'outcome':1},{'probability':1.01,'outcome':1},{'probability':.5,'outcome':.5}]:
            with self.assertRaises(ValueError):calibration_bins([row])

if __name__=='__main__':unittest.main()
