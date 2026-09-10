"""Export historical usage only after exact personnel and identity audit matching."""
import hashlib
import json
from pathlib import Path
from publication import write_receipts

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('playerId', 'name', 'team', 'season', 'type', 'week')


def key(row, identity=False):
    return (row['playerId'], row['reportTeam' if identity else 'team'], row['season'], row['type'], row['week'])


def indexed(rows, identity=False):
    result = {key(r, identity): r for r in rows}
    if len(result) != len(rows):
        raise ValueError('Duplicate player-scope rows')
    return result


def build_payload(personnel, usage, identity, personnel_hash):
    if usage['personnelArtifactHash'] != personnel_hash or identity['inputHashes']['personnel'] != personnel_hash:
        raise ValueError('Audit does not match exact current personnel input')
    players = indexed(personnel['players'])
    uses, ids = indexed(usage['records']), indexed(identity['records'], True)
    if set(players) != set(uses) or set(players) != set(ids):
        raise ValueError('Audit player scope differs')
    records = []
    for k, player in players.items():
        u, i = uses[k], ids[k]
        if any(player[f] != u[f] for f in FIELDS) or i['name'] != player['name']:
            raise ValueError('Audit player identity differs')
        value = u['usage'] if i['status'] == 'matched' else {
            'status': 'unavailable', 'reason': 'Historical identity not corroborated'}
        records.append({f: player[f] for f in FIELDS} | {'identityStatus': i['status'], 'usage': value})
    return {'schemaVersion': 1, 'personnelSourceHash': personnel['sourceHash'],
            'personnelRetrievedAt': personnel['retrievedAt'], 'personnelArtifactHash': personnel_hash,
            'sourceSeason': usage['sourceSeason'], 'calculatedAt': usage['generatedAt'],
            'snapSourceHash': usage['snapSourceHash'], 'registrySourceHash': usage['registrySourceHash'],
            'meaning': 'Historical appearance-conditioned usage, not current availability, projected snaps or player value.',
            'records': records}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    personnel_path = ROOT / 'data/personnel.json'
    usage_path = ROOT / 'reviews/player-usage-audit.json'
    identity_path = ROOT / 'reviews/personnel-identity-audit.json'
    personnel, usage, identity = [json.loads(p.read_text(encoding='utf-8-sig')) for p in (personnel_path, usage_path, identity_path)]
    if usage['scheduleHash'] != digest(ROOT / 'data/games.csv'):
        raise ValueError('Usage schedule has changed')
    if any(digest(ROOT / 'scripts' / name) != value for name, value in usage['codeHashes'].items()):
        raise ValueError('Usage calculation code has changed')
    if identity['codeHash'] != digest(ROOT / 'scripts/audit_personnel_identity.py'):
        raise ValueError('Identity calculation code has changed')
    output = build_payload(personnel, usage, identity, digest(personnel_path))
    output['auditHashes'] = {'usage': digest(usage_path), 'identity': digest(identity_path)}
    write_receipts(ROOT / 'data/player-usage.json', output)
    print(json.dumps({'records': len(output['records']), 'available': sum(r['usage']['status'] == 'available' for r in output['records'])}))


if __name__ == '__main__':
    main()
