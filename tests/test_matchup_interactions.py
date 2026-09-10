import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from experiment_matchup import interactions,fit_correction
from experiment_model import features

class MatchupInteractionTests(unittest.TestCase):
    def test_pairing_and_swap_symmetry(self):
        home=np.arange(1,15,dtype=float);away=np.arange(21,35,dtype=float)
        x=np.r_[1,0,home-away,home+away]
        expected=np.array([home[i]*home[i+7]-away[i]*away[i+7] for i in [0,1,3]])
        np.testing.assert_allclose(interactions(x),expected)
        np.testing.assert_allclose(interactions(np.r_[1,0,away-home,home+away]),-expected)
        np.testing.assert_allclose(interactions(np.r_[1,0,np.zeros(14),2*home]),np.zeros(3))
    def test_training_scale_and_fixed_penalty(self):
        x=np.diag([2.,4.,6.]);beta,scale=fit_correction(x,np.array([13.,26.,39.]))
        np.testing.assert_allclose(scale,np.array([2,4,6])/np.sqrt(3))
        np.testing.assert_allclose(x@beta,[3.,6.,9.])
        zero,_=fit_correction(np.zeros((3,3)),np.ones(3))
        np.testing.assert_allclose(zero,np.zeros(3))
    def test_current_week_stats_cannot_change_current_week_interactions(self):
        rows=[{'game_id':str(i),'season':2024,'week':week,'game_type':'REG','gameday':day,'home_team':'DEN','away_team':'KC','location':'Neutral'} for i,week,day in [(1,1,'2024-09-01'),(2,2,'2024-09-08'),(3,2,'2024-09-09')]]
        stats={(r['game_id'],team):np.arange(1,8,dtype=float)*(1 if team=='DEN' else 2) for r in rows for team in ['DEN','KC']}
        before,_=features(rows,stats,90)
        stats[('2','DEN')]=np.ones(7)*10000
        stats[('3','KC')]=np.ones(7)*-10000
        after,_=features(rows,stats,90)
        np.testing.assert_allclose(before,after)
        np.testing.assert_allclose(interactions(before[1]),interactions(after[1]))

if __name__=='__main__':unittest.main()
