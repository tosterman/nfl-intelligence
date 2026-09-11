"""Build a deterministic weather publication bundle after retained-source replay."""
import hashlib
import json
from pathlib import Path
from weather_history import build as replay_history
from venue_evidence import validate_venue
from refresh_weather import parse_time

ROOT = Path(__file__).resolve().parents[1]


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def fingerprint(value):
    return hashlib.sha256(encode(value)).hexdigest()


def build(root=ROOT):
    def read(name): return json.loads((root / 'data' / name).read_bytes())
    weather, history, site = read('weather.json'), read('weather-history.json'), read('site.json')
    if replay_history(root) != history:
        raise ValueError('Weather history differs from retained-source replay')
    started, generated = parse_time(weather['collectionStartedAt']), parse_time(weather['generatedAt'])
    if started > generated:
        raise ValueError('Invalid weather collection interval')
    venues, extra = read('weather-venues.json'), read('weather-osm-venues.json')
    if any(venues[k].get('status') != 'unavailable' for k in venues.keys() & extra.keys()):
        raise ValueError('Conflicting venue registry')
    venues.update(extra)
    for venue in venues.values(): validate_venue(venue)
    games = {game['id']: game for game in site['games']}
    if len(games) != len(site['games']) or set(games) != set(weather['games']):
        raise ValueError('Weather game context scope differs')
    ledger = read('weather-ledger.json')
    retained = {record['hash']: record for record in ledger}
    contexts = {}
    for identity, record in weather['games'].items():
        game = games[identity]
        if record['gameId'] != identity or any(record.get(k) != game.get(k) for k in ('kickoff', 'venue')):
            raise ValueError('Weather game context changed')
        contexts[identity] = {k: game.get(k) for k in ('id', 'season', 'kickoff', 'venue', 'neutral')}
        if record['status'] == 'available':
            venue = venues.get(game['venue'])
            if game.get('neutral') or not venue or record.get('locationEvidence') != venue:
                raise ValueError('Weather venue context changed')
            if 'validFromSeason' in venue and game['season'] < venue['validFromSeason']:
                raise ValueError('Weather venue season changed')
            if not started <= parse_time(record['retrievedAt']) <= generated:
                raise ValueError('Observation outside weather collection interval')
            digest = fingerprint(record)
            if retained.get(digest) != {**record, 'hash': digest}:
                raise ValueError('Current weather observation is not retained')
    payload = {'schemaVersion': 1, 'weather': weather, 'history': history, 'contexts': contexts,
               'venueRegistryHash': fingerprint(venues)}
    sources = sorted({record[key] for record in ledger for key in ('pointHash', 'sourceHash')})
    manifest = {'schemaVersion': 1, 'validatorVersion': 'weather-bundle-v1',
                'collectionStartedAt': weather['collectionStartedAt'], 'generatedAt': weather['generatedAt'],
                'payloadSha256': fingerprint(payload), 'payloadBytes': len(encode(payload)),
                'venueRegistryHash': payload['venueRegistryHash'], 'sourceHashes': sources,
                'ledgerSha256': fingerprint(ledger)}
    return {'manifest': manifest, 'payload': payload}


if __name__ == '__main__':
    result = build()
    output = ROOT / 'release-recovery/weather-bundle.json'
    output.parent.mkdir(exist_ok=True)
    output.write_bytes(encode(result) + b'\n')
    print(json.dumps(result['manifest'], indent=2))
