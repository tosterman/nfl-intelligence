"""Offline historical weekly context replay from exact retained source bytes."""
import hashlib
import json
from pathlib import Path
import socket
from scripts.weekly_matchup_context import from_retained


def main():
    def forbidden(*args, **kwargs):
        raise RuntimeError('Network disabled during replay')
    socket.create_connection = forbidden
    socket.socket.connect = forbidden
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'data/explosive-source.json').read_text())
    adjudications = json.loads((root / 'data/red-zone-adjudications.json').read_text())
    results = []
    for week in (2, 10, 18):
        result = from_retained(root, manifest, adjudications, week)
        assert result['status'] == 'available'
        for kind, fields in [('passing', ['plays', 'explosive']), ('rushing', ['plays', 'explosive']),
                             ('inside20', ['possessions', 'touchdowns'])]:
            for field in fields:
                assert sum(t['offense'][kind][field] for t in result['teams'].values()) == sum(t['defense'][kind][field] for t in result['teams'].values())
        canonical = json.dumps(result, sort_keys=True, separators=(',', ':')).encode()
        row = {'week': week, 'cutoff': result['cutoff'], 'games': len(result['gameIds']),
               'teams': len(result['teams']), 'sha256': hashlib.sha256(canonical).hexdigest(),
               'offenseTotals': {kind: {field: sum(t['offense'][kind][field] for t in result['teams'].values()) for field in fields}
                                 for kind, fields in [('passing', ['plays', 'explosive']), ('rushing', ['plays', 'explosive']), ('inside20', ['possessions', 'touchdowns'])]}}
        results.append(row)
        print(json.dumps(row), flush=True)
    report = {'sourceSha256': manifest['plays']['sha256'], 'scheduleSha256': manifest['schedule']['sha256'],
              'results': results, 'limitations': 'Historical vintage, current-season component only. No prospective availability or forecast improvement established.'}
    (root / 'reviews/weekly-matchup-replay.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
