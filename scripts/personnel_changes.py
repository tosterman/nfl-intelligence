"""Observed source changes, not medical event dates or canonical cross-feed IDs."""
import gzip
import hashlib
import json
import re
from pathlib import Path
from refresh_personnel import normalize, timestamp

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('name', 'position', 'reportStatus', 'practiceStatus', 'reportInjury', 'practiceInjury', 'practiceSecondaryInjury')


def identity(row):
    return tuple(row[k] for k in ('season', 'type', 'week', 'team', 'playerId'))


def changes(before, after):
    start, end = timestamp(before['retrievedAt']), timestamp(after['retrievedAt'])
    if start >= end:
        raise ValueError('Captures must be strictly ordered')
    def index(snapshot):
        rows = {identity(r): r for r in snapshot['players']}
        if len(rows) != len(snapshot['players']):
            raise ValueError('Duplicate scoped player identity')
        return rows
    old, new = index(before), index(after)
    result = []
    for key in sorted(old.keys() | new.keys()):
        a, b = old.get(key), new.get(key)
        fields = {f: {'before': a.get(f) if a else None, 'after': b.get(f) if b else None}
                  for f in FIELDS if a is None or b is None or a.get(f) != b.get(f)}
        if not fields:
            continue
        result.append(dict(zip(('season', 'type', 'week', 'team', 'playerId'), key)) | {
            'kind': 'first-observed' if a is None else 'no-longer-present' if b is None else 'changed',
            'observedAfter': before['retrievedAt'], 'observedBy': after['retrievedAt'],
            'eventTime': None, 'playerName': (b or a)['name'], 'position': (b or a).get('position'), 'fields': fields,
        })
    return result


def load_capture(path, folder):
    raw = gzip.decompress(path.read_bytes())
    capture_hash = hashlib.sha256(raw).hexdigest()
    if path.name != capture_hash + '.snapshot.json.gz':
        raise ValueError('Capture identity mismatch')
    snapshot = json.loads(raw)
    if snapshot.get('schemaVersion') != 1 or not isinstance(snapshot.get('sourceHash'), str) or not re.fullmatch(r'[a-f0-9]{64}', snapshot['sourceHash']):
        raise ValueError('Invalid source reference')
    source = gzip.decompress((folder / (snapshot['sourceHash'] + '.csv.gz')).read_bytes())
    if hashlib.sha256(source).hexdigest() != snapshot['sourceHash']:
        raise ValueError('Source identity mismatch')
    if snapshot['status'] != 'available' or timestamp(snapshot['assetUpdatedAt']) > timestamp(snapshot['retrievedAt']):
        raise ValueError('Invalid capture chronology')
    rows = normalize(source, snapshot['season'], {r['team'] for r in snapshot['players']})
    if rows != snapshot['players']:
        raise ValueError('Capture does not reproduce source normalization')
    return snapshot | {'captureHash': capture_hash}


def main():
    folder = ROOT / 'data/personnel-sources'
    captures = sorted((load_capture(p, folder) for p in folder.glob('*.snapshot.json.gz')),
                      key=lambda s: timestamp(s['retrievedAt']))
    if not captures:
        raise ValueError('No verified captures')
    transitions = []
    for before, after in zip(captures, captures[1:]):
        transitions.append({'beforeCapture': before['captureHash'], 'afterCapture': after['captureHash'],
                            'changes': changes(before, after)})
    report = {'schemaVersion': 1, 'identityNamespace': 'nflverse injury-feed GSIS ID within season/type/week/team',
              'codeHashes': {name: hashlib.sha256((ROOT / 'scripts' / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() for name in ('personnel_changes.py', 'refresh_personnel.py')},
              'interpretation': 'Observed feed differences only. Missing rows do not establish availability. Event times and cross-feed identity mappings are unknown.',
              'baseline': {'captureHash': captures[0]['captureHash'], 'retrievedAt': captures[0]['retrievedAt'], 'rows': len(captures[0]['players'])},
              'captures': [{k: s[k] for k in ('captureHash', 'sourceHash', 'retrievedAt', 'assetUpdatedAt')} for s in captures],
              'transitions': transitions}
    current = json.loads((ROOT / 'data/personnel.json').read_bytes())
    current_hash = hashlib.sha256((json.dumps(current, sort_keys=True, separators=(',', ':')) + '\n').encode()).hexdigest()
    if current_hash != captures[-1]['captureHash']:
        raise ValueError('Current personnel snapshot differs from latest verified capture')
    public = {'schemaVersion': 1, 'sourceHash': current['sourceHash'], 'retrievedAt': current['retrievedAt'],
              'previousRetrievedAt': captures[-2]['retrievedAt'] if len(captures) > 1 else None,
              'changes': transitions[-1]['changes'] if transitions else []}
    (ROOT / 'data/personnel-changes.json').write_text(json.dumps(public, indent=2)+'\n')
    (ROOT / 'reviews/personnel-change-ledger.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'captures': len(captures), 'transitions': len(transitions), 'changes': sum(len(t['changes']) for t in transitions)}))


if __name__ == '__main__':
    main()
