"""Separate scrimmage possession evidence from touchdown conversion sequences.

Exploratory helper: callers still need schedule cutoffs, coverage and ownership
validation before publishing red-zone rates.
"""
import math


def possession_rows(rows):
    result = []
    seen = set()
    ended = False
    for row in rows:
        try:
            identity = float(row['play_id'])
        except (ValueError, TypeError):
            raise ValueError('Invalid play identity') from None
        if not math.isfinite(identity) or identity < 0 or identity in seen:
            raise ValueError('Invalid or duplicate play identity')
        seen.add(identity)
        if ended:
            continue
        kind = row['play_type']
        if kind == 'no_play':
            # Source-classified nullified plays cannot themselves score. Their
            # pre-snap location still describes the possession before a TD.
            if row.get('touchdown') not in ('', '0'):
                raise ValueError('Contradictory no-play scoring state')
            if row.get('two_point_attempt') != '1' and row.get('extra_point_attempt') != '1':
                result.append(row)
            continue
        if kind not in ('pass', 'run', 'no_play', 'qb_kneel', 'qb_spike', 'field_goal', 'punt', 'kickoff'):
            continue
        for flag in ('touchdown', 'two_point_attempt', 'extra_point_attempt'):
            if row.get(flag) not in ('0', '1'):
                raise ValueError(f'Unknown {flag} state')
        if row['two_point_attempt'] == '1' or row['extra_point_attempt'] == '1':
            continue
        if kind != 'kickoff':
            result.append(row)
        # Defensive and return touchdowns also end the original possession.
        if row['touchdown'] == '1':
            ended = True
    return result


def drive_evidence(rows):
    plays = possession_rows(rows)
    owned = [r for r in plays if r.get('posteam')]
    if not owned:
        return None
    owners = {r['posteam'] for r in owned}
    defenders = {r['defteam'] for r in owned}
    if len(owners) != 1 or len(defenders) != 1 or owners == defenders or '' in defenders:
        raise ValueError('Ambiguous possession participants')
    offense, defense = next(iter(owners)), next(iter(defenders))
    entry = None
    for row in owned:
        position = row.get('yardline_100')
        if position in ('', None) and row['play_type'] == 'no_play':
            continue
        try:
            position = float(position)
        except (ValueError, TypeError):
            raise ValueError('Unknown field position') from None
        if not math.isfinite(position) or not 0 <= position <= 100:
            raise ValueError('Invalid field position')
        if entry is None and 0 < position < 20:
            entry = row['play_id']
    touchdowns = [r for r in owned if r['touchdown'] == '1']
    if any(r['td_team'] not in (offense, defense) for r in touchdowns):
        raise ValueError('Unknown scoring team')
    scored = any(r['td_team'] == offense for r in touchdowns)
    allowed = any(r['td_team'] == defense for r in touchdowns)
    outcomes = {r['fixed_drive_result'] for r in rows if r.get('fixed_drive_result')}
    if len(outcomes) != 1:
        raise ValueError('Ambiguous drive result')
    outcome = next(iter(outcomes))
    if (outcome == 'Touchdown') != scored or (outcome == 'Opp touchdown') != allowed:
        raise ValueError('Play scoring and drive result disagree')
    return {'offense': offense, 'defense': defense, 'inside20': entry is not None,
            'entryPlayId': entry, 'offensiveTouchdown': scored, 'result': outcome}
