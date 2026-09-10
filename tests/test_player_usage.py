import sys,unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from player_usage import prior_usage
class PlayerUsageTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,9,10,tzinfo=timezone.utc)
        self.registry=[{'gsis_id':'g','pfr_id':'p'}]
        self.games={'old':{'kickoff':self.now-timedelta(days=100),'teams':['A','B'],'completed':True}}
        self.row={'game_id':'old','pfr_player_id':'p','team':'A','opponent':'B','offense_pct':'0.5','defense_pct':'0','st_pct':'0.1','offense_snaps':'30','defense_snaps':'0','st_snaps':'2'}
    def test_old_team_and_absent_history_are_not_current_role_or_zero(self):
        result=prior_usage('g',self.registry,[self.row],self.games,self.now)
        self.assertEqual(result['historicalTeams'],['A']);self.assertEqual(result['weightedShares']['offense_pct'],.5)
        self.assertEqual(result['appearances'],1);self.assertEqual(result['daysSinceLastAppearance'],100)
        self.assertEqual(prior_usage('g',self.registry,[],self.games,self.now)['status'],'unavailable')
    def test_embargo_and_duplicate_id_guards(self):
        self.games['old']['kickoff']=self.now-timedelta(hours=24)
        self.assertEqual(prior_usage('g',self.registry,[self.row],self.games,self.now)['status'],'unavailable')
        self.assertEqual(prior_usage('g',self.registry+[{'gsis_id':'other','pfr_id':'p'}],[self.row],self.games,self.now)['status'],'unavailable')
    def test_malformed_team_share_and_duplicate_game_fail(self):
        for rows in [[self.row,self.row],[{**self.row,'offense_pct':'NaN'}],[{**self.row,'team':'C'}]]:
            with self.assertRaises(ValueError):prior_usage('g',self.registry,rows,self.games,self.now)

    def test_ninety_day_half_life_and_missing_games_are_not_zeros(self):
        games={**self.games,'recent':{**self.games['old'],'kickoff':self.now-timedelta(days=10)},'missing':{**self.games['old'],'kickoff':self.now-timedelta(days=5)}}
        rows=[{**self.row,'offense_pct':'0.2'},{**self.row,'game_id':'recent','offense_pct':'0.8'}]
        result=prior_usage('g',self.registry,rows,games,self.now)
        self.assertAlmostEqual(result['weightedShares']['offense_pct'],.6)
        self.assertEqual(result['appearances'],2)

    def test_only_last_eight_appearances_in_time_order(self):
        games={str(i):{**self.games['old'],'kickoff':self.now-timedelta(days=i+2)} for i in range(10)}
        rows=[{**self.row,'game_id':str(i),'offense_pct':'1' if i<8 else '0'} for i in reversed(range(10))]
        result=prior_usage('g',self.registry,rows,games,self.now)
        self.assertEqual([r['gameId'] for r in result['games']],[str(i) for i in range(8)])
        self.assertEqual(result['weightedShares']['offense_pct'],1)
        for limit in [0,-1,9,1.5,True]:
            with self.assertRaises(ValueError):prior_usage('g',self.registry,rows,games,self.now,limit)

if __name__=='__main__':unittest.main()
