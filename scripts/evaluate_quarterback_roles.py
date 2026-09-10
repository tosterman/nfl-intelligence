"""Retrospective role/source-coverage audit, not a model accuracy evaluation."""
import bisect,csv,hashlib,json
from collections import defaultdict,Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from depth_chart import instant,quarterbacks_before

ROOT=Path(__file__).resolve().parents[1]
EXPECTED='f5a4aa3fa70150e810b2255200c8735a6c1cc8ff77361308ce39149345b39b4a'

def main():
    path=ROOT/'release-recovery/depth_charts_2025.csv'
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=EXPECTED:raise ValueError('Re-audit source metadata before evaluating different bytes')
    groups=defaultdict(lambda:defaultdict(list))
    with path.open(encoding='utf-8-sig',newline='') as source:
        for row in csv.DictReader(source):groups[row['team']][instant(row['dt'])].append(row)
    times={team:sorted(values) for team,values in groups.items()}
    schedule_path=ROOT/'data/games.csv'
    with schedule_path.open(encoding='utf-8-sig',newline='') as source:
        games=[g for g in csv.DictReader(source) if g['season']=='2025' and g['home_score'] and g['away_score']]
    observations=[]
    for hours in (24,0):
        for game in games:
            if not game['gametime']:raise ValueError('Missing kickoff must not silently leave denominator')
            kickoff=datetime.fromisoformat(game['gameday']+'T'+game['gametime']).replace(tzinfo=ZoneInfo('America/New_York')).astimezone(timezone.utc)
            cutoff=kickoff-timedelta(hours=hours)
            for side in ('away','home'):
                team=game[side+'_team'];clock=times.get(team,[])
                index=bisect.bisect_left(clock,cutoff)-1
                rows=groups[team][clock[index]] if index>=0 else []
                selected=quarterbacks_before(rows,{team},cutoff)[team]
                recorded=game[side+'_qb_id'] or None
                status='missing_game_qb' if not recorded else ('unavailable_chart' if selected['status']!='available' else ('match' if selected['listedFirst']==recorded else 'different'))
                observations.append({'gameId':game['game_id'],'gameType':game['game_type'],'team':team,'hoursBeforeKickoff':hours,'cutoff':cutoff.isoformat(),
                    'chartRecordedAt':selected['recordedAt'],'listedFirst':selected['listedFirst'],'gameQb':recorded,'result':status,'unavailableReason':selected.get('reason')})
    summaries={}
    for hours in (24,0):
        counts=Counter(r['result'] for r in observations if r['hoursBeforeKickoff']==hours)
        eligible=counts['match']+counts['different']
        summaries[str(hours)]={'teamGames':sum(counts.values()),'counts':dict(counts),'matchRateAmongComparable':counts['match']/eligible if eligible else None,
            'comparableCoverage':eligible/sum(counts.values()) if counts else None}
    output={'evaluatedAt':datetime.now(timezone.utc).isoformat(),'season':2025,'games':len(games),'maximumChartAgeHours':30,
        'depthSourceUrl':'https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2025.csv','depthSourceHash':digest,
        'scheduleHash':hashlib.sha256(schedule_path.read_bytes()).hexdigest(),'summaries':summaries,'observations':observations,
        'limitations':'Retrospective provider timestamps and current corrected schedule. Matching role IDs is not proof of pregame starter confirmation or predictive improvement.'}
    (ROOT/'reviews/quarterback-role-evaluation.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(summaries,indent=2))

if __name__=='__main__':main()
