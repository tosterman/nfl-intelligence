"""Offline collection feasibility; never schedules jobs or spends API credits."""
import hashlib,json,math
from datetime import datetime,timedelta,timezone
from pathlib import Path


def plan(start,end,kickoffs,max_gap=timedelta(hours=5,minutes=30),cooldown=timedelta(minutes=30),lead=timedelta(minutes=5)):
    if end<=start or cooldown<=timedelta() or max_gap<cooldown or not timedelta()<lead<=timedelta(minutes=15):
        raise ValueError('Invalid planning limits')
    # Leave the selected execution lead before kickoff. Share a request only
    # when every grouped kickoff has a common acceptable acquisition window.
    groups=[]
    for kickoff in sorted(set(kickoffs)):
        if not start<kickoff<=end:continue
        lo=max(start,kickoff-timedelta(minutes=15));hi=kickoff-lead
        if lo>hi:raise ValueError('Kickoff too close to planning start')
        if groups and lo<=groups[-1]['hi']:
            groups[-1]['lo']=lo;groups[-1]['kickoffs'].append(kickoff)
        else:groups.append({'lo':lo,'hi':hi,'kickoffs':[kickoff]})
    following=None
    for group in reversed(groups):
        at=group['hi'] if following is None else min(group['hi'],following-cooldown)
        if at<group['lo']:raise ValueError('Closing windows conflict with collection cooldown')
        group['at']=at;following=at
    anchors=sorted(set([start]+[g['at'] for g in groups]))
    requests=[start]
    for left,right in zip(anchors,anchors[1:]):
        duration=right-left
        count=math.ceil(duration/max_gap)
        if duration/count<cooldown:raise ValueError('Anchor spacing conflicts with collection cooldown')
        requests.extend(left+duration*i/count for i in range(1,count+1))
    while end-requests[-1]>max_gap:
        requests.append(requests[-1]+max_gap)
    return requests,groups


def main():
    root=Path(__file__).resolve().parents[1]
    raw=(root/'data/site.json').read_bytes();site=json.loads(raw)
    start=datetime.now(timezone.utc);end=start+timedelta(days=31)
    kicks=[datetime.fromisoformat(g['kickoff'].replace('Z','+00:00')) for g in site['games'] if g.get('kickoff')]
    requests,groups=plan(start,end,kicks)
    gaps=[(b-a).total_seconds()/60 for a,b in zip(requests,requests[1:])]
    report={'checkedAt':start.isoformat(),'through':end.isoformat(),'scheduleHash':hashlib.sha256(raw).hexdigest(),
      'scenario':'Hypothetical empty-budget start; includes initial request and keeps coverage through the horizon.',
      'requests':len(requests),'remainingFrom155':155-len(requests),'minimumGapMinutes':min(gaps),'maximumGapMinutes':max(gaps),
      'closingGroups':len(groups),'nominallyCoveredKickoffs':sum(len(g['kickoffs']) for g in groups),
      'requestTimes':[t.isoformat() for t in requests],
      'closingWindows':[{'acquireAt':g['at'].isoformat(),'kickoffs':[k.isoformat() for k in g['kickoffs']]} for g in groups],
      'limitations':['Not an executable schedule or optimality proof.','Existing rolling usage, retries and manual requests consume the same budget.','Scheduler delay can violate cooldown or closing windows.','Bookmaker update time must independently pass freshness checks.','Forecast publication eligibility is independent of quote coverage.']}
    (root/'reviews/odds-cadence-feasibility.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('requestTimes','closingWindows')}))

if __name__=='__main__':main()
