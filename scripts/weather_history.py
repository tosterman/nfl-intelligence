"""Replay retained NWS responses into compact, publication-ready history."""
import gzip
import hashlib
import json
import sys
from pathlib import Path
from refresh_weather import kickoff_period, parse_time
from venue_evidence import validate_venue

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('status', 'gameId', 'kickoff', 'venue', 'issuedAt', 'retrievedAt', 'periodStart',
          'periodEnd', 'temperature', 'temperatureUnit', 'precipitationProbability',
          'windSpeed', 'windDirection', 'summary', 'sourceHash', 'hash')


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def repository_json_hash(payload):
    # Git stores these text artifacts with LF; Windows checkouts may use CRLF.
    # Raw upstream NWS response hashes are never normalized.
    return digest(payload.replace(b'\r\n', b'\n'))


def source(root, identity):
    if not isinstance(identity, str) or len(identity) != 64 or any(c not in '0123456789abcdef' for c in identity):
        raise ValueError('Invalid weather source identity')
    payload = gzip.decompress((root / 'data/weather-sources' / (identity + '.json.gz')).read_bytes())
    if digest(payload) != identity:
        raise ValueError('Weather source fingerprint mismatch')
    return json.loads(payload)


def verify_record(record, root):
    original = {k: v for k, v in record.items() if k != 'hash'}
    if digest(json.dumps(original, sort_keys=True, separators=(',', ':')).encode()) != record['hash']:
        raise ValueError('Weather observation fingerprint mismatch')
    location = record['locationEvidence']
    if location.get('status') not in ('confirmed-address-geocode', 'confirmed-osm-stadium', 'confirmed-official-linked-place'):
        raise ValueError('Unverified weather location')
    validate_venue(location)
    if any(record[axis] != location[axis] for axis in ('latitude', 'longitude')):
        raise ValueError('Weather location changed')
    expected_point = f"https://api.weather.gov/points/{record['latitude']:.4f},{record['longitude']:.4f}"
    if record['pointUrl'] != expected_point:
        raise ValueError('Weather lookup location mismatch')
    point = source(root, record['pointHash'])
    if point['properties']['forecastHourly'] != record['sourceUrl']:
        raise ValueError('Weather forecast URL mismatch')
    replay = kickoff_period(source(root, record['sourceHash']), parse_time(record['kickoff']), parse_time(record['retrievedAt']))
    if record['status'] != 'available' or parse_time(record['retrievedAt']) >= parse_time(record['kickoff']):
        raise ValueError('Invalid pregame observation')
    if any(record.get(key) != value for key, value in replay.items()):
        raise ValueError('Weather fields differ from retained response')
    # Exact location evidence identity avoids merging distinct location methods.
    result = {key: record.get(key) for key in FIELDS}
    result['locationHash'] = digest(json.dumps(location, sort_keys=True, separators=(',', ':')).encode())
    return result


def build(root=ROOT):
    payload = (root / 'data/weather-ledger.json').read_bytes()
    rows = [verify_record(record, root) for record in json.loads(payload)]
    if len({r['hash'] for r in rows}) != len(rows):
        raise ValueError('Duplicate weather observations')
    return {'schemaVersion': 1, 'ledgerHash': repository_json_hash(payload),
            'weatherHash': repository_json_hash((root / 'data/weather.json').read_bytes()), 'records': rows}


def main():
    result = build()
    path = ROOT / 'data/weather-history.json'
    if '--check' in sys.argv:
        if json.loads(path.read_text()) != result:
            raise ValueError('Published weather history does not match retained evidence')
    else:
        temporary = path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(result, indent=2) + '\n')
        temporary.replace(path)
    print(f"Verified {len(result['records'])} retained weather observations")


if __name__ == '__main__':
    main()
