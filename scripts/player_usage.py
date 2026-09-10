"""Historical appearance-conditioned snap shares, not predicted player value."""
import math
from datetime import timedelta

def prior_usage(gsis_id,registry,snaps,games,cutoff,limit=8):
    if isinstance(limit,bool) or not isinstance(limit,int) or not 1<=limit<=8:raise ValueError('Appearance limit must be an integer from one to eight')
    people=[r for r in registry if r['gsis_id']==gsis_id]
    unknown=lambda reason:{'status':'unavailable','reason':reason}
    if len(people)!=1 or not people[0].get('pfr_id'):return unknown('Missing or ambiguous registry identity')
    pfr=people[0]['pfr_id']
    if sum(r.get('pfr_id')==pfr for r in registry)!=1:return unknown('PFR identity shared by multiple registry rows')
    eligible=[];seen=set()
    for row in snaps:
        if row['pfr_player_id']!=pfr:continue
        game=games.get(row['game_id'])
        if not game or game['kickoff']+timedelta(hours=24)>=cutoff:continue
        if not game['completed']:continue
        if row['team'] not in game['teams'] or row['opponent'] not in game['teams'] or row['team']==row['opponent']:raise ValueError('Snap team disagrees with schedule')
        if row['game_id'] in seen:raise ValueError('Duplicate player-game snap record')
        seen.add(row['game_id'])
        values={k:float(row[k]) for k in ['offense_pct','defense_pct','st_pct','offense_snaps','defense_snaps','st_snaps']}
        if any(not math.isfinite(v) or v<0 or (k.endswith('_pct') and v>1) or (k.endswith('_snaps') and v!=int(v)) for k,v in values.items()):raise ValueError('Invalid snap usage')
        if sum(values[k] for k in ['offense_snaps','defense_snaps','st_snaps'])==0:continue
        eligible.append({'gameId':row['game_id'],'team':row['team'],'kickoff':game['kickoff'],'values':values})
    recent=sorted(eligible,key=lambda r:(r['kickoff'],r['gameId']),reverse=True)[:limit]
    if not recent:return unknown('No eligible historical appearances')
    # A common rescaling preserves relative weights without underflow for old histories.
    weights=[2**(-((recent[0]['kickoff']-r['kickoff']).total_seconds()/86400)/90) for r in recent]
    total=sum(weights)
    return {'status':'available','pfrId':pfr,'appearances':len(recent),'lastAppearance':recent[0]['kickoff'].isoformat(),
        'daysSinceLastAppearance':(cutoff-recent[0]['kickoff']).total_seconds()/86400,
        'historicalTeams':sorted({r['team'] for r in recent}),
        'weightedShares':{k:sum(w*r['values'][k] for w,r in zip(weights,recent))/total for k in ['offense_pct','defense_pct','st_pct']},
        'games':[{**r,'kickoff':r['kickoff'].isoformat()} for r in recent],
        'meaning':'Recency-weighted shares in up to eight recorded appearances; missing games are not zero-filled. Historical teams may differ from current team. Not expected snaps, injury impact or player quality.'}
