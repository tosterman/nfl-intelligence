"""Verify personnel publication contexts against the edition's exact schedule."""
import csv
import hashlib
import io
from build_data import kickoff, team


def verify_schedule(edition, raw):
    if hashlib.sha256(raw).hexdigest() != edition.get('source', {}).get('sha256'):
        raise ValueError('Edition schedule digest differs')
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    required = {'game_id', 'season', 'week', 'game_type', 'home_team', 'away_team',
                'gameday', 'gametime', 'stadium', 'location'}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError('Schedule context columns missing')
    contexts = {}
    for row in reader:
        if int(row['season']) != edition['season']:
            continue
        if row['game_id'] in contexts:
            raise ValueError('Duplicate schedule game scope')
        contexts[row['game_id']] = {
            'id': row['game_id'], 'season': int(row['season']), 'week': int(row['week']),
            'type': row['game_type'], 'home': team(row['home_team']), 'away': team(row['away_team']),
            'kickoff': kickoff(row).isoformat() if row['gametime'] else None,
            'venue': row['stadium'], 'neutral': row['location'] == 'Neutral',
        }
    games = edition['games']
    if len(games) != len(contexts) or {g['id'] for g in games} != set(contexts):
        raise ValueError('Edition schedule game scope differs')
    for game in games:
        if any(game.get(field) != value for field, value in contexts[game['id']].items()):
            raise ValueError('Edition schedule game context differs')
    return contexts
