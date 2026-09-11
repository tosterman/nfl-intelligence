"""Offline phase reconciliation, not a publication of red-zone rates."""
import collections
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
from red_zone_possessions import possession_rows

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'data/explosive-source.json').read_text())
    source = manifest['plays']
    raw = (ROOT / source['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != source['sha256']:
        raise ValueError('Retained source digest mismatch')
    groups = collections.defaultdict(list)
    for row in csv.DictReader(io.StringIO(gzip.decompress(raw).decode())):
        groups[(row['game_id'], row['fixed_drive'])].append(row)
    counts = collections.Counter()
    rejected, ambiguous, disagreements = [], [], []
    for (game, drive), rows in groups.items():
        identity = {'gameId': game, 'fixedDrive': drive}
        try:
            valid = possession_rows(rows)
        except ValueError as error:
            rejected.append({**identity, 'reason': str(error)})
            continue
        owners = sorted({r['posteam'] for r in valid if r['posteam']})
        if len(owners) > 1:
            ambiguous.append({**identity, 'owners': owners})
        reached = any(r['yardline_100'] and 0 < float(r['yardline_100']) < 20 for r in valid)
        provider = any(r['drive_inside20'] == '1' for r in rows)
        counts[f'observed={reached},provider={provider}'] += 1
        if reached != provider:
            disagreements.append(identity)
    report = {'sourceSha256': source['sha256'], 'groups': len(groups),
              'definition': 'Pre-snap field position strictly inside 20, ending at any touchdown; source row order preserved',
              'comparison': dict(counts), 'rejected': rejected,
              'ambiguousOwners': ambiguous, 'disagreements': disagreements,
              'publicationReady': False}
    (ROOT / 'reviews/red-zone-phase-reconciliation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__': main()
