import sys,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from plan_odds_cadence import plan

class CadenceTests(unittest.TestCase):
    def test_earlier_collection_can_tolerate_five_minute_jitter_with_shorter_cooldown(self):
        from stress_odds_cadence import simulate
        start=datetime(2026,9,1,tzinfo=timezone.utc);k=start+timedelta(hours=10)
        kicks=[k,k+timedelta(minutes=20)]
        requests,groups=plan(start,start+timedelta(days=2),kicks,cooldown=timedelta(minutes=20),lead=timedelta(minutes=10))
        for parity in (0,1):
            events=[(t+timedelta(minutes=5 if i%2==parity else 0),True) for i,t in enumerate(requests)]
            r=simulate(start,start+timedelta(days=2),events,kicks,cooldown_minutes=15)
            self.assertEqual(r['coveredKickoffs'],2);self.assertEqual(r['cooldownBlocked'],0)

    def test_close_kickoffs_share_only_a_common_window(self):
        start=datetime(2026,9,1,tzinfo=timezone.utc);k=start+timedelta(hours=10)
        requests,groups=plan(start,start+timedelta(days=2),[k,k,k+timedelta(minutes=5),k+timedelta(minutes=25)])
        self.assertEqual(len(groups),2)
        for kickoff in [k,k+timedelta(minutes=5),k+timedelta(minutes=25)]:
            self.assertTrue(any(kickoff-timedelta(minutes=15)<=at<=kickoff-timedelta(minutes=5) for at in requests))
        for a,b in zip(requests,requests[1:]):
            self.assertGreaterEqual(b-a,timedelta(minutes=30));self.assertLessEqual(b-a,timedelta(hours=5,minutes=30))

    def test_incompatible_windows_are_rejected(self):
        start=datetime(2026,9,1,tzinfo=timezone.utc);k=start+timedelta(hours=10)
        with self.assertRaises(ValueError):plan(start,start+timedelta(days=2),[k,k+timedelta(minutes=15),k+timedelta(minutes=30)])

    def test_no_games_still_requires_regular_refresh(self):
        start=datetime(2026,9,1,tzinfo=timezone.utc)
        requests,groups=plan(start,start+timedelta(days=31),[])
        self.assertEqual(groups,[]);self.assertEqual(requests[0],start)
        self.assertLessEqual(start+timedelta(days=31)-requests[-1],timedelta(hours=5,minutes=30))
        self.assertLessEqual(max(b-a for a,b in zip(requests,requests[1:])),timedelta(hours=5,minutes=30))
