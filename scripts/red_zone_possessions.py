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
        if kind not in ('kickoff', 'punt'):
            result.append(row)
        # Defensive and return touchdowns also end the original possession.
        if row['touchdown'] == '1':
            ended = True
    return result
