"""Offline alternate cooldown experiment; production reservation stays unchanged."""
import hashlib,json
from datetime import datetime,timedelta
from pathlib import Path
from plan_odds_cadence import plan
from stress_odds_cadence import simulate

def main():
    root=Path(__file__).resolve().parents[1]
    original_raw=(root/'reviews/odds-cadence-feasibility.json').read_bytes();original=json.loads(original_raw)
    raw=(root/'data/site.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=original['scheduleHash']:raise ValueError('Schedule differs from fixed comparison input')
    start=datetime.fromisoformat(original['checkedAt']);end=datetime.fromisoformat(original['through'])
    kicks=sorted({datetime.fromisoformat(g['kickoff'].replace('Z','+00:00')) for g in json.loads(raw)['games'] if g.get('kickoff')})
    kicks=[k for k in kicks if start<k<=end]
    times,groups=plan(start,end,kicks,cooldown=timedelta(minutes=20),lead=timedelta(minutes=10))
    first=groups[0]['at']
    scenarios={
      'on-time':([(t,True) for t in times],()),
      'all-five-minutes-late':([(t+timedelta(minutes=5),True) for t in times],()),
      'alternating-five-minutes-late-even':([(t+timedelta(minutes=5 if i%2==0 else 0),True) for i,t in enumerate(times)],()),
      'alternating-five-minutes-late-odd':([(t+timedelta(minutes=5 if i%2 else 0),True) for i,t in enumerate(times)],()),
      'first-closing-request-fails':([(t,t!=first) for t in times],()),
      'ten-prior-attempts':([(t,True) for t in times],tuple(start-timedelta(hours=i+1) for i in range(10))),
    }
    report={'originalPlanHash':hashlib.sha256(original_raw).hexdigest(),'scheduleHash':original['scheduleHash'],
      'productionChanged':False,'candidateCooldownMinutes':15,'plannedMinimumGapMinutes':20,'plannedLeadMinutes':10,
      'requestCount':len(times),'remainingFrom155':155-len(times),'requestTimes':[t.isoformat() for t in times],
      'scenarios':{name:simulate(start,end,events,kicks,prior,cooldown_minutes=15) for name,(events,prior) in scenarios.items()},
      'limitations':['Requires a separately reviewed change from the production thirty-minute acquisition cooldown.','Fixed hypothetical delay scenarios do not establish real scheduler reliability.','No retry or rescheduling; successful requests assume fresh quotes and immediate upload.','Actual rolling attempt history remains required before live activation.']}
    (root/'reviews/odds-cadence-alternative.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='requestTimes'},indent=2))

if __name__=='__main__':main()
