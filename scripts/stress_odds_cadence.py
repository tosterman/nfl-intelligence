"""Deterministic hypothetical delay/failure scenarios; no provider requests."""
import hashlib,json
from datetime import datetime,timedelta
from pathlib import Path


def simulate(start,end,events,kickoffs,prior_attempts=(),limit=155):
    attempts=sorted(prior_attempts)
    if end<=start or any(t>=start for t in attempts):raise ValueError('Invalid scenario chronology')
    successful=[];cooldown=budget=failed=accepted=0
    for at,ok in sorted(events):
        if not start<=at<=end:continue
        recent=[t for t in attempts if at-t<timedelta(days=31)]
        if recent and at-recent[-1]<timedelta(minutes=30):cooldown+=1;continue
        if len(recent)>=limit:budget+=1;continue
        attempts.append(at);accepted+=1
        if ok:successful.append(at)
        else:failed+=1
    # Optimistic: every successful request has a new bookmaker quote and an
    # immediate storage upload. Real quote freshness can only reduce coverage.
    covered=sum(any(k-timedelta(minutes=15)<=at<k for at in successful) for k in set(kickoffs))
    stale=timedelta();fresh_until=start
    for at in successful:
        if at>fresh_until:stale+=at-fresh_until
        fresh_until=max(fresh_until,at+timedelta(hours=6))
    if end>fresh_until:stale+=end-fresh_until
    return {'acceptedAttempts':accepted,'failedRequests':failed,'cooldownBlocked':cooldown,'budgetBlocked':budget,
            'coveredKickoffs':covered,'totalKickoffs':len(set(kickoffs)),'staleMinutes':stale.total_seconds()/60}


def main():
    root=Path(__file__).resolve().parents[1];raw=(root/'reviews/odds-cadence-feasibility.json').read_bytes();plan=json.loads(raw)
    start=datetime.fromisoformat(plan['checkedAt']);end=datetime.fromisoformat(plan['through'])
    times=list(map(datetime.fromisoformat,plan['requestTimes']))
    kicks=[datetime.fromisoformat(k) for g in plan['closingWindows'] for k in g['kickoffs']]
    first_close=datetime.fromisoformat(plan['closingWindows'][0]['acquireAt'])
    scenarios={
      'on-time':([(t,True) for t in times],()),
      'all-five-minutes-late':([(t+timedelta(minutes=5),True) for t in times],()),
      'alternating-five-minutes-late':([(t+timedelta(minutes=5 if i%2==0 else 0),True) for i,t in enumerate(times)],()),
      'first-closing-request-fails':([(t,t!=first_close) for t in times],()),
      'ten-prior-attempts':([(t,True) for t in times],tuple(start-timedelta(hours=i+1) for i in range(10))),
    }
    report={'planHash':hashlib.sha256(raw).hexdigest(),'scenarios':{name:simulate(start,end,events,kicks,prior) for name,(events,prior) in scenarios.items()},
      'limitations':['Constructed scenarios, not measured scheduler delay rates or expected performance.','No retries or dynamic rescheduling.','Successful requests assume instantaneous fresh quotes and uploads.','Prior requests consume budget but provide no initial usable feed in this simulation.','Live acquisition configuration remains unchanged.']}
    (root/'reviews/odds-cadence-stress.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
