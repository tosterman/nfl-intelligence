import sys,unittest
from pathlib import Path
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from stress_odds_cadence import simulate

class StressTests(unittest.TestCase):
    def test_failure_consumes_budget_and_cooldown_but_not_freshness(self):
        s=datetime(2026,9,1,tzinfo=timezone.utc)
        r=simulate(s,s+timedelta(hours=1),[(s,False),(s+timedelta(minutes=10),True),(s+timedelta(minutes=30),True)],[],limit=1)
        self.assertEqual((r['acceptedAttempts'],r['failedRequests'],r['cooldownBlocked'],r['budgetBlocked']),(1,1,1,1))
        self.assertEqual(r['staleMinutes'],60)

    def test_quote_at_kickoff_is_not_a_closing_observation(self):
        s=datetime(2026,9,1,tzinfo=timezone.utc);k=s+timedelta(hours=1)
        self.assertEqual(simulate(s,k,[(k,True)],[k])['coveredKickoffs'],0)
        self.assertEqual(simulate(s,k,[(k-timedelta(minutes=15),True)],[k])['coveredKickoffs'],1)

    def test_rolling_budget_releases_exactly_at_window_end(self):
        s=datetime(2026,9,1,tzinfo=timezone.utc)
        r=simulate(s,s+timedelta(hours=1),[(s,True)],[],[s-timedelta(days=31)],limit=1)
        self.assertEqual(r['acceptedAttempts'],1)
