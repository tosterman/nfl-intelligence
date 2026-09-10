"""Reject incomplete forecast editions before publishing through Git."""
from datetime import datetime, timezone
from publication import context_matches, snapshot_valid


def instant(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Publication timestamps require timezones')
    return parsed


def validate_forecast_edition(site, ledger, *, now=None):
    generated = instant(site['generatedAt'])
    clock = now or datetime.now(timezone.utc)
    if clock.tzinfo is None or generated > clock:
        raise ValueError('Edition generation time must not be in the future')
    canonical = {s['hash']: s for s in ledger}
    if len(canonical) != len(ledger):
        raise ValueError('Duplicate canonical snapshot hashes')
    games = site['games']
    if len({g['id'] for g in games}) != len(games):
        raise ValueError('Duplicate game IDs in edition')
    verified = 0
    for game in games:
        kickoff = instant(game['kickoff']) if game.get('kickoff') else None
        required = (game['season'] == site['season'] and game['week'] == site['week']
                    and kickoff is not None and kickoff > generated)
        snapshot = game.get('snapshot')
        if snapshot is None:
            if required:
                raise ValueError('Current-week future game lacks a forecast; regenerate edition')
            continue
        if (snapshot.get('gameId') != game['id'] or not context_matches(snapshot, game)
                or not snapshot_valid(snapshot)):
            raise ValueError('Displayed forecast is invalid or lacks matching game context; regenerate edition')
        if canonical.get(snapshot['hash']) != snapshot or snapshot not in game.get('history', []):
            raise ValueError('Displayed forecast is not retained in canonical ledger and game history')
        created = instant(snapshot['generatedAt'])
        if kickoff is None or created >= kickoff or created > generated:
            raise ValueError('Displayed forecast has invalid pregame generation time')
        if required and snapshot.get('modelVersion') != site['modelVersion']:
            raise ValueError('Current-week forecast uses a different model version')
        verified += 1
    return verified
