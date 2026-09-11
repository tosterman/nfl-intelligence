"""Offline v1-to-v2 migration. Does not publish or replace existing archives."""
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from weather_bundle import ROOT, build, encode, fingerprint, transport
from refresh_weather import parse_time

MAX_JSON_BYTES = 2_000_000
MAX_SOURCE_BYTES = 2_000_000


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def snapshot_transport(verified, ledger):
    """Reuse the verified bundle codec with only current observation anchors."""
    retained = {row['hash']: row for row in ledger}
    anchors = {row['hash']: row for row in verified['history']['records']}
    identities = sorted(fingerprint(record) for record in verified['weather']['games'].values()
                        if record['status'] == 'available')
    current = [retained[identity] for identity in identities]
    payload = {'schemaVersion': 1, 'weather': verified['weather'], 'contexts': verified['contexts'],
               'venueRegistryHash': verified['venueRegistryHash'],
               'history': {'schemaVersion': 1, 'records': [anchors[identity] for identity in identities]}}
    manifest = {'schemaVersion': 1, 'validatorVersion': 'weather-bundle-v1',
                'collectionStartedAt': verified['weather']['collectionStartedAt'],
                'generatedAt': verified['weather']['generatedAt'],
                'payloadSha256': fingerprint(payload), 'payloadBytes': len(encode(payload)),
                'venueRegistryHash': verified['venueRegistryHash'],
                'sourceHashes': sorted({row[key] for row in current for key in ('pointHash', 'sourceHash')}),
                'ledgerSha256': fingerprint(current)}
    return transport({'manifest': manifest, 'payload': payload}).decode()


def build_partitions(root=ROOT):
    verified = build(root)['payload']
    ledger = json.loads((root / 'data/weather-ledger.json').read_bytes())
    history = {row['hash']: row for row in verified['history']['records']}
    grouped = defaultdict(list)
    for row in ledger:
        grouped[row['gameId']].append(row)
    objects = {}

    def retain(raw, limit=MAX_JSON_BYTES):
        if not 0 < len(raw) <= limit:
            raise ValueError('Weather partition object exceeds size limit')
        identity = digest(raw)
        objects[identity] = raw
        return {'sha256': identity, 'bytes': len(raw)}

    games = {}
    for game, rows in sorted(grouped.items()):
        rows.sort(key=lambda row: row['hash'])
        sources = {}
        for identity in sorted({row[key] for row in rows for key in ('pointHash', 'sourceHash')}):
            raw = (root / 'data/weather-sources' / (identity + '.json.gz')).read_bytes()
            if digest(gzip.decompress(raw)) != identity:
                raise ValueError('Weather source fingerprint changed')
            sources[identity] = retain(raw, MAX_SOURCE_BYTES)
        partition = {'schemaVersion': 2, 'kind': 'weather-game-history', 'gameId': game,
                     # Keep Python number serialization intact across JS transports.
                     'ledgerJson': encode(rows).decode(),
                     'history': {'schemaVersion': 1, 'records': [history[row['hash']] for row in rows]},
                     'sources': sources}
        games[game] = retain(encode(partition))
    snapshot = {'schemaVersion': 2, 'kind': 'weather-snapshot',
                'bundleJson': snapshot_transport(verified, ledger)}
    publication = {'schemaVersion': 2, 'kind': 'weather-publication',
                   'generatedAt': verified['weather']['generatedAt'],
                   'snapshot': retain(encode(snapshot)),
                   'index': retain(encode({'schemaVersion': 2, 'kind': 'weather-index', 'games': games}))}
    return {'publication': retain(encode(publication)), 'objects': objects}


def verify_migration(root, result):
    """Traverse references and compare all contents with replayed original evidence."""
    verified = build(root)['payload']
    ledger = json.loads((root / 'data/weather-ledger.json').read_bytes())
    grouped = defaultdict(list)
    for row in ledger:
        grouped[row['gameId']].append(row)
    history = {row['hash']: row for row in verified['history']['records']}
    visited = set()

    def read(ref, kind=None):
        if not isinstance(ref, dict) or set(ref) != {'sha256', 'bytes'}:
            raise ValueError('Invalid migration reference')
        identity, size = ref['sha256'], ref['bytes']
        if not isinstance(identity, str) or type(size) is not int or not 0 < size <= MAX_JSON_BYTES:
            raise ValueError('Invalid migration reference size')
        raw = result['objects'].get(identity)
        if not isinstance(raw, bytes) or len(raw) != size or digest(raw) != identity:
            raise ValueError('Missing or corrupt migration object')
        visited.add(identity)
        if kind is None:
            return raw
        value = json.loads(raw)
        if not isinstance(value, dict) or value.get('schemaVersion') != 2 or value.get('kind') != kind:
            raise ValueError('Invalid migration object kind')
        return value

    publication = read(result['publication'], 'weather-publication')
    if publication.get('generatedAt') != verified['weather']['generatedAt']:
        raise ValueError('Migration acquisition time differs')
    snapshot = read(publication['snapshot'], 'weather-snapshot')
    if snapshot.get('bundleJson') != snapshot_transport(verified, ledger):
        raise ValueError('Migration snapshot differs')
    index = read(publication['index'], 'weather-index')
    if set(index.get('games', {})) != set(grouped):
        raise ValueError('Migration game index differs')
    source_hashes = set()
    for game, ref in index['games'].items():
        partition = read(ref, 'weather-game-history')
        rows = sorted(grouped[game], key=lambda row: row['hash'])
        if partition.get('gameId') != game or partition.get('ledgerJson') != encode(rows).decode():
            raise ValueError('Migration observations differ')
        expected_history = {'schemaVersion': 1, 'records': [history[row['hash']] for row in rows]}
        if encode(partition.get('history')) != encode(expected_history):
            raise ValueError('Migration history differs')
        expected_sources = {row[key] for row in rows for key in ('pointHash', 'sourceHash')}
        if set(partition.get('sources', {})) != expected_sources:
            raise ValueError('Migration source references differ')
        for identity, source_ref in partition['sources'].items():
            raw = read(source_ref)
            original = (root / 'data/weather-sources' / (identity + '.json.gz')).read_bytes()
            if raw != original or digest(gzip.decompress(raw)) != identity:
                raise ValueError('Migration source bytes differ')
            source_hashes.add(identity)
    return {'observations': len(ledger), 'games': len(grouped), 'sources': len(source_hashes),
            'reachableObjects': len(visited), 'snapshotBytes': publication['snapshot']['bytes'],
            'indexBytes': publication['index']['bytes'],
            'largestPartitionBytes': max((ref['bytes'] for ref in index['games'].values()), default=0)}


def verify_partition_continuity(previous, current):
    """Append-only comparison, separate from raw-source and snapshot validation."""
    def read(result, ref, kind):
        if not isinstance(ref, dict) or set(ref) != {'sha256', 'bytes'}:
            raise ValueError('Invalid partition continuity reference')
        raw = result['objects'].get(ref['sha256'])
        if not isinstance(raw, bytes) or type(ref['bytes']) is not int or not 0 < len(raw) <= MAX_JSON_BYTES or len(raw) != ref['bytes'] or digest(raw) != ref['sha256']:
            raise ValueError('Partition continuity integrity failure')
        value = json.loads(raw)
        if not isinstance(value, dict) or value.get('schemaVersion') != 2 or value.get('kind') != kind:
            raise ValueError('Partition continuity schema differs')
        return value
    old_root = read(previous, previous['publication'], 'weather-publication')
    new_root = read(current, current['publication'], 'weather-publication')
    old_time, new_time = parse_time(old_root['generatedAt']), parse_time(new_root['generatedAt'])
    if new_time < old_time or (new_time == old_time and previous['publication'] != current['publication']):
        raise ValueError('Older or conflicting weather publication')
    old_index = read(previous, old_root['index'], 'weather-index')['games']
    new_index = read(current, new_root['index'], 'weather-index')['games']
    if not set(old_index) <= set(new_index):
        raise ValueError('Retained weather game removed')
    changed = 0
    for game, old_ref in old_index.items():
        if old_ref == new_index[game]:
            continue
        changed += 1
        old = read(previous, old_ref, 'weather-game-history')
        new = read(current, new_index[game], 'weather-game-history')
        if old.get('gameId') != game or new.get('gameId') != game:
            raise ValueError('Weather partition game differs')
        for old_rows, new_rows in [(json.loads(old['ledgerJson']), json.loads(new['ledgerJson'])),
                                   (old['history']['records'], new['history']['records'])]:
            indexed = {row['hash']: row for row in new_rows}
            if len(indexed) != len(new_rows) or len({row['hash'] for row in old_rows}) != len(old_rows):
                raise ValueError('Duplicate partition observations')
            if any(row['hash'] not in indexed or encode(row) != encode(indexed[row['hash']]) for row in old_rows):
                raise ValueError('Retained weather observation removed or changed')
        if any(identity not in new['sources'] or ref != new['sources'][identity] for identity, ref in old['sources'].items()):
            raise ValueError('Retained weather source removed or changed')
    return {'previousGames': len(old_index), 'currentGames': len(new_index), 'changedGames': changed}


def main():
    result = build_partitions()
    summary = verify_migration(ROOT, result)
    folder = ROOT / 'release-recovery/weather-v2-migration'
    folder.mkdir(parents=True, exist_ok=True)
    for identity, raw in result['objects'].items():
        path = folder / identity
        if path.exists() and path.read_bytes() != raw:
            raise ValueError('Existing local migration object differs')
        if not path.exists():
            with path.open('xb') as stream:
                stream.write(raw)
    report = {'publication': result['publication'], **summary, 'storageWrites': False}
    (folder / 'report.json').write_bytes(encode(report) + b'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
