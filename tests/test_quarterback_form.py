import sys,unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from quarterback_form import prior_passing,form

class QuarterbackFormTests(unittest.TestCase):
    def setUp(self):
        self.cutoff=datetime(2026,9,10,18,tzinfo=timezone.utc)
        self.game={'gameday':'2026-09-08','gametime':'13:00','home_score':'0','away_score':'7','home_team':'CHI','away_team':'CAR'}
        self.row={'game_id':'g','player_id':'p','position':'QB','team':'CHI','attempts':'20','sacks_suffered':'2','passing_yards':'150','sack_yards_lost':'-10'}
    def test_negative_sack_yards_reduce_net_passing(self):
        prior=prior_passing([self.row],{'g':self.game},self.cutoff)
        result=form(prior,'p',self.cutoff,prior_dropbacks=0)
        self.assertAlmostEqual(result['netYardsPerDropback'],140/22)
        self.assertAlmostEqual(result['sackRate'],2/22)
    def test_future_and_embargo_boundary_excluded(self):
        for day in ['2026-09-09','2026-09-10','2026-09-11']:
            game=self.game|{'gameday':day,'gametime':'14:00'}
            self.assertEqual(prior_passing([self.row],{'g':game},self.cutoff),[])
    def test_missing_history_stays_unknown(self):
        result=form([], 'new-player',self.cutoff)
        self.assertIsNone(result['netYardsPerDropback'])
    def test_duplicate_and_wrong_team_rejected(self):
        with self.assertRaises(ValueError):prior_passing([self.row,self.row],{'g':self.game},self.cutoff)
        with self.assertRaises(ValueError):prior_passing([self.row|{'team':'DAL'}],{'g':self.game},self.cutoff)
    def test_future_stat_values_do_not_change_prior_feature(self):
        original=prior_passing([self.row],{'g':self.game},self.cutoff)
        future=self.row|{'game_id':'future','passing_yards':'9999'}
        games={'g':self.game,'future':self.game|{'gameday':'2026-09-11'}}
        self.assertEqual(original,prior_passing([self.row,future],games,self.cutoff))

    def test_decay_and_population_prior_arithmetic(self):
        prior=[{'playerId':'p','at':self.cutoff-timedelta(days=2),'dropbacks':20,'netYards':100,'sacks':2},
               {'playerId':'other','at':self.cutoff-timedelta(days=92),'dropbacks':40,'netYards':400,'sacks':0}]
        weight=2**(-2/90)
        # Older player's weight is exactly half: population rate is (100+200)/(20+20).
        result=form(prior,'p',self.cutoff)
        self.assertAlmostEqual(result['weightedDropbacks'],20*weight)
        self.assertAlmostEqual(result['netYardsPerDropback'],(100*weight+200*7.5)/(20*weight+200))
        self.assertAlmostEqual(result['sackRate'],0.1)

if __name__=='__main__':unittest.main()
