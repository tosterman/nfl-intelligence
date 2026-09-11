"""Weekly descriptive context from retained bytes; no numerical forecast effect."""
import csv
from datetime import date, datetime
import gzip
import hashlib
import io
import json
import math

from scripts.explosive_plays import summarize
from scripts.build_red_zone_evidence import summarize_drives
from scripts.pbp_adjudications import apply_adjudications


def weekly_context(plays, schedule, season, week, game_type):
    """Freeze at the earliest scheduled date in an exact season/type/week."""
    if type(season) is not int or type(week) is not int or week < 1 or game_type not in ('REG', 'POST'):
        raise ValueError('Invalid weekly scope')
    selected = [g for g in schedule if g['season'] == str(season)]
    scope = [g for g in selected if g['game_type'] == game_type and g['week'] == str(week)]
    if not scope:
        raise ValueError('Weekly schedule scope missing')
    cutoff = min(date.fromisoformat(g['gameday']) for g in scope).isoformat()
    # Date alone is insufficient if a postponed game from this week is recorded
    # anomalously before the boundary. Explicit week/type eligibility is retained.
    def prior(g):
        return ((g['game_type'] == 'REG' and (game_type == 'POST' or int(g['week']) < week))
                or (g['game_type'] == 'POST' == game_type and int(g['week']) < week))
    eligible = {g['game_id'] for g in selected if prior(g) and g['gameday'] < cutoff
                and all(g.get(k) not in ('', None, 'NA') for k in ('home_score', 'away_score'))}
    gated = [g if g['game_id'] in eligible else {**g, 'home_score': '', 'away_score': ''} for g in selected]
    for game in selected:
        if game['game_id'] not in eligible:
            continue
        rows = [r for r in plays if r['game_id'] == game['game_id']]
        terminal = [r for r in rows if r.get('desc') == 'END GAME']
        if len(terminal) != 1 or terminal[0].get('play_type') != '':
            raise ValueError('Completed-game terminal coverage missing')
        ids = [float(r['play_id']) for r in rows]
        # IDs identify plays; inserted/corrected rows can have larger IDs than
        # the terminal record. Preserve the source's chronological row order.
        if not all(math.isfinite(i) and i >= 0 for i in ids) or terminal[0] is not rows[-1]:
            raise ValueError('Invalid terminal play ordering')
        for side in ('home', 'away'):
            final = float(terminal[0].get(f'total_{side}_score', 'nan'))
            if not math.isfinite(final) or final < 0 or final != int(final) or final != float(game[f'{side}_score']):
                raise ValueError('Terminal score differs from schedule')
    big_plays = summarize(plays, gated, cutoff)
    expected = {(g['game_id'], team) for g in selected if g['game_id'] in eligible
                for team in (g['home_team'], g['away_team'])}
    if {(r['gameId'], r['offense']) for r in big_plays} != expected:
        raise ValueError('Weekly big-play coverage incomplete')
    drives = summarize_drives(plays, gated, cutoff, season)
    teams = {}
    for row in big_plays:
        for side, team in [('offense', row['offense']), ('defense', row['defense'])]:
            counts = teams.setdefault(team, {}).setdefault(side, {
                'gameIds': [], 'passing': {'plays': 0, 'explosive': 0},
                'rushing': {'plays': 0, 'explosive': 0}, 'inside20': {'possessions': 0, 'touchdowns': 0}})
            counts['gameIds'].append(row['gameId'])
            for kind in ('passing', 'rushing'):
                for field in ('plays', 'explosive'):
                    counts[kind][field] += row[kind][field]
    for drive in drives:
        if drive['inside20']:
            for side, team in [('offense', drive['offense']), ('defense', drive['defense'])]:
                counts = teams[team][side]['inside20']
                counts['possessions'] += 1
                counts['touchdowns'] += int(drive['offensiveTouchdown'])
    return {'season': season, 'week': week, 'gameType': game_type, 'cutoff': cutoff,
            'status': 'available' if eligible else 'no-eligible-games',
            'gameIds': sorted(eligible), 'teams': dict(sorted(teams.items()))}


def from_retained(root, manifest, adjudications, week, game_type='REG'):
    retained = datetime.fromisoformat(manifest['retainedAt'].replace('Z', '+00:00'))
    if retained.tzinfo is None:
        raise ValueError('Source observation must include timezone')
    def read(key):
        raw = (root / manifest[key]['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != manifest[key]['sha256']:
            raise ValueError('Retained source digest mismatch')
        return list(csv.DictReader(io.StringIO(gzip.decompress(raw).decode('utf-8-sig'))))
    schedule = read('schedule')
    plays = apply_adjudications(read('plays'), manifest['plays']['sha256'], adjudications)
    result = weekly_context(plays, schedule, manifest['season'], week, game_type)
    return {'schemaVersion': 1, **result, 'sourceObservedAt': manifest['retainedAt'],
            'sourceSha256': manifest['plays']['sha256'], 'scheduleSha256': manifest['schedule']['sha256'],
            'adjudicationHash': hashlib.sha256(json.dumps(adjudications, sort_keys=True).encode()).hexdigest(),
            'limitations': 'Historical source vintage. Cutoff restricts game eligibility, not original data availability. No forecast adjustment.'}
