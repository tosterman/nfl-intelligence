"""Select recorded quarterback roles strictly before a cutoff, without starter inference."""
from datetime import datetime, timedelta

def instant(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Depth-chart timestamp lacks timezone')
    return parsed

def quarterbacks_before(rows, teams, cutoff, maximum_age_hours=30):
    """Newest team snapshot wins, including snapshots with no quarterback rows."""
    if cutoff.tzinfo is None or maximum_age_hours <= 0:
        raise ValueError('Invalid cutoff or freshness limit')
    latest = {}
    selected = {}
    for row in rows:
        team = row['team']
        if team not in teams:
            continue
        at = instant(row['dt'])
        if at >= cutoff:
            continue
        if team not in latest or at > latest[team]:
            latest[team] = at
            selected[team] = []
        if at == latest[team] and row['pos_abb'] == 'QB':
            selected[team].append(row)
    result = {}
    for team in sorted(teams):
        at = latest.get(team)
        unknown = {'status': 'unavailable', 'recordedAt': at.isoformat() if at else None, 'quarterbacks': [], 'listedFirst': None}
        if at is None or cutoff-at >= timedelta(hours=maximum_age_hours):
            result[team] = unknown | {'reason': 'No recent prior depth chart'}
            continue
        players, seen, identities = [], set(), set()
        invalid = False
        for row in selected[team]:
            try:
                rank = int(row['pos_rank'])
                key = (row['pos_grp_id'], row['pos_slot'], rank)
                identity = (row['pos_grp_id'], row['pos_slot'], row['gsis_id'])
                if rank < 1 or key in seen or identity in identities or not row['gsis_id'] or not row['player_name'].strip():
                    raise ValueError('Ambiguous quarterback identity or rank')
                seen.add(key)
                identities.add(identity)
                players.append({'playerId': row['gsis_id'], 'name': row['player_name'], 'rank': rank,
                                'formationId': row['pos_grp_id'], 'slot': row['pos_slot']})
            except (ValueError, KeyError, TypeError):
                invalid = True
        leaders = {p['playerId'] for p in players if p['rank'] == 1}
        if invalid or len(leaders) != 1:
            result[team] = unknown | {'reason': 'Missing or conflicting quarterback ranks'}
            continue
        result[team] = {'status': 'available', 'recordedAt': at.isoformat(), 'quarterbacks': sorted(players, key=lambda p: (p['rank'],p['formationId'],p['slot'])),
                        'listedFirst': next(iter(leaders)), 'meaning': 'Listed depth-chart role; not a confirmed game starter'}
    return result
