"""Descriptive credited-yardage counts. No forecast adjustments or fitted rates."""
from datetime import date
import math


def summarize(plays, schedule, cutoff):
    boundary = date.fromisoformat(cutoff)
    games = {}
    for game in schedule:
        if game['game_id'] in games:
            raise ValueError('Duplicate schedule game')
        games[game['game_id']] = game
    counts, seen = {}, set()
    for play in plays:
        game = games.get(play['game_id'])
        if game is None:
            raise ValueError('Play has no matching schedule game')
        if date.fromisoformat(game['gameday']) >= boundary:
            continue
        if any(game.get(key) in ('', None, 'NA') for key in ('home_score', 'away_score')):
            continue
        identity = (play['game_id'], play['play_id'])
        if not play['play_id'] or identity in seen:
            raise ValueError('Duplicate or missing play identity')
        seen.add(identity)
        if play['game_date'] != game['gameday']:
            raise ValueError('Play and schedule dates differ')
        kind = play['play_type']
        if kind not in ('pass', 'run'):
            continue
        if any(play.get(flag) not in ('0', '1') for flag in ('qb_kneel', 'qb_spike')):
            raise ValueError('Missing kneel/spike classification')
        if play['qb_kneel'] == '1' or play['qb_spike'] == '1':
            continue
        offense, defense = play['posteam'], play['defteam']
        if offense == defense or {offense, defense} != {game['home_team'], game['away_team']}:
            raise ValueError('Play participants differ from schedule')
        try:
            yards = float(play['yards_gained'])
        except (ValueError, TypeError):
            raise ValueError('Invalid credited yardage') from None
        if not math.isfinite(yards) or not -100 <= yards <= 100 or yards != int(yards):
            raise ValueError('Invalid credited yardage')
        key = (play['game_id'], offense)
        if key not in counts:
            counts[key] = {'gameId': play['game_id'], 'date': game['gameday'],
                           'offense': offense, 'defense': defense,
                           'passing': {'plays': 0, 'explosive': 0},
                           'rushing': {'plays': 0, 'explosive': 0}}
        bucket = counts[key]['passing' if kind == 'pass' else 'rushing']
        bucket['plays'] += 1
        bucket['explosive'] += int(yards >= (20 if kind == 'pass' else 10))
    return [counts[key] for key in sorted(counts)]
