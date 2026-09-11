"""Season-scoped participation; separate from accepted prior-season calculations."""
from player_usage import prior_usage

def season_phase(kind):
    return 'POST' if kind in {'WC', 'DIV', 'CON', 'SB'} else kind

def season_usage(gsis_id, registry, snaps, games, cutoff, season, kind, week, current_team):
    """Appearance evidence for earlier weeks of one season, split by team tenure."""
    phases = {'REG': 1, 'POST': 2}
    if (kind not in phases or isinstance(season, bool) or not isinstance(season, int)
            or isinstance(week, bool) or not isinstance(week, int) or week < 1
            or cutoff.tzinfo is None or not current_team):
        raise ValueError('Invalid participation context')
    eligible_games = {}
    for identity, game in games.items():
        game = {**game, 'type': season_phase(game.get('type'))}
        if game.get('season') != season or game.get('type') not in phases:
            continue
        prior_week = game.get('week')
        if isinstance(prior_week, bool) or not isinstance(prior_week, int) or prior_week < 1:
            raise ValueError('Invalid schedule week')
        if (phases[game['type']], prior_week) < (phases[kind], week):
            eligible_games[identity] = game
    eligible_rows = []
    for row in snaps:
        game = eligible_games.get(row['game_id'])
        if game is None:
            continue
        if (str(row.get('season')) != str(season) or str(row.get('week')) != str(game['week'])
                or row.get('game_type') != game['type']):
            raise ValueError('Participation source scope disagrees with schedule')
        eligible_rows.append(row)
    def summarize(rows):
        return prior_usage(gsis_id, registry, rows, eligible_games, cutoff)
    return {'season': season, 'type': kind, 'week': week, 'cutoff': cutoff.isoformat(),
            'overall': summarize(eligible_rows),
            'currentTeam': summarize([r for r in eligible_rows if r['team'] == current_team]),
            'formerTeams': summarize([r for r in eligible_rows if r['team'] != current_team])}
