"""Prior quarterback passing features for research; no production score adjustment."""
import math
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo

def prior_passing(rows,games,cutoff):
    if cutoff.tzinfo is None:raise ValueError('Timezone-aware cutoff required')
    result=[];seen=set()
    for row in rows:
        if row['position']!='QB':continue
        game=games.get(row['game_id'])
        if not game or not game['gametime'] or not game['home_score'] or not game['away_score']:continue
        at=datetime.fromisoformat(game['gameday']+'T'+game['gametime']).replace(tzinfo=ZoneInfo('America/New_York')).astimezone(timezone.utc)
        # Historical files have no per-stat publication time: conservative proxy, not a vintage replay.
        if at+timedelta(hours=24)>=cutoff:continue
        if row['team'] not in (game['home_team'],game['away_team']):raise ValueError('Player game/team mismatch')
        key=(row['game_id'],row['player_id'])
        if key in seen:raise ValueError('Duplicate player game')
        seen.add(key)
        attempts,sacks,yards,sack_yards=[float(row[k]) for k in ('attempts','sacks_suffered','passing_yards','sack_yards_lost')]
        if not all(math.isfinite(v) for v in (attempts,sacks,yards,sack_yards)) or attempts<0 or sacks<0 or attempts%1 or sacks%1 or sack_yards>0:
            raise ValueError('Invalid passing totals or sack-yard sign')
        dropbacks=attempts+sacks
        if dropbacks==0:continue
        result.append({'playerId':row['player_id'],'gameId':row['game_id'],'at':at,'dropbacks':dropbacks,'netYards':yards+sack_yards,'sacks':sacks})
    return result

def form(prior,player_id,cutoff,half_life_days=90,prior_dropbacks=200):
    if half_life_days<=0 or prior_dropbacks<0:raise ValueError('Invalid smoothing parameters')
    weighted=[]
    for row in prior:
        age=(cutoff-row['at']).total_seconds()/86400
        if age<=1:raise ValueError('Performance row violates publication embargo')
        weighted.append((row,2**(-age/half_life_days)))
    league_n=sum(r['dropbacks']*w for r,w in weighted)
    league_y=sum(r['netYards']*w for r,w in weighted)
    selected=[(r,w) for r,w in weighted if r['playerId']==player_id]
    if not selected or league_n==0:return {'status':'unavailable','games':0,'weightedDropbacks':0,'netYardsPerDropback':None,'sackRate':None}
    n=sum(r['dropbacks']*w for r,w in selected)
    return {'status':'available','games':len(selected),'weightedDropbacks':n,
            'netYardsPerDropback':(sum(r['netYards']*w for r,w in selected)+prior_dropbacks*league_y/league_n)/(n+prior_dropbacks),
            'sackRate':sum(r['sacks']*w for r,w in selected)/n,
            'latestGameAt':max(r['at'] for r,w in selected).isoformat()}
