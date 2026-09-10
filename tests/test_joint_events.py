import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_joint_events import event_scores,events

class JointEventTests(unittest.TestCase):
    def test_known_mass_and_observation(self):
        mass=np.zeros((61,61));mass[20,17]=.4;mass[17,20]=.1;mass[35,14]=.2;mass[30,30]=.3
        r=event_scores(mass,20,17)
        self.assertAlmostEqual(r['margin3']['probability'],.5)
        self.assertEqual(r['margin3']['observed'],1)
        self.assertAlmostEqual(r['margin3']['brier'],.25)
        self.assertAlmostEqual(r['margin21plus']['probability'],.2)
        self.assertAlmostEqual(r['total60plus']['probability'],.3)
        self.assertEqual(r['total30orless']['probability'],0)
        self.assertEqual(r,event_scores(mass.T,17,20))

    def test_inclusive_boundaries(self):
        self.assertTrue(events(15,15)['total30orless'])
        self.assertFalse(events(16,15)['total30orless'])
        self.assertTrue(events(30,30)['total60plus'])
        self.assertFalse(events(30,29)['total60plus'])
        self.assertTrue(events(28,7)['margin21plus'])
        self.assertFalse(events(27,7)['margin21plus'])
        for n in [3,7,10,14]:self.assertTrue(events(0,n)['margin'+str(n)])

    def test_invalid_distribution_or_outcome_fails(self):
        mass=np.ones((4,4))/16
        for bad in [mass*2,mass*np.nan,-mass]:
            with self.assertRaises(ValueError):event_scores(bad,0,3)
        for h,a in [(0,4),(-1,0),(.5,0),(np.nan,0)]:
            with self.assertRaises(ValueError):event_scores(mass,h,a)

if __name__=='__main__':unittest.main()
