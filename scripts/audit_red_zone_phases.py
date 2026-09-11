"""Offline phase reconciliation, not a publication of red-zone rates."""
import collections
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
from red_zone_possessions import possession_rows, drive_evidence
from pbp_adjudications import apply_adjudications

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'data/explosive-source.json').read_text())
    source = manifest['plays']
    raw = (ROOT / source['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != source['sha256']:
        raise ValueError('Retained source digest mismatch')
    groups = collections.defaultdict(list)
    adjudications = json.loads((ROOT / 'data/red-zone-adjudications.json').read_text())
    source_rows = list(csv.DictReader(io.StringIO(gzip.decompress(raw).decode())))
    for row in apply_adjudications(source_rows, source['sha256'], adjudications):
        groups[(row['game_id'], row['fixed_drive'])].append(row)
    counts = collections.Counter()
    rejected, ambiguous, disagreements = [], [], []
    outcome_counts = collections.Counter()
    outcome_rejected = []
    official_sample = collections.defaultdict(lambda: {'possessions': 0, 'touchdowns': 0})
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
        try:
            outcome = drive_evidence(rows)
        except ValueError as error:
            outcome_rejected.append({**identity, 'reason': str(error)})
            continue
        if outcome:
            outcome_counts['possessions'] += 1
            if outcome['inside20']:
                outcome_counts['inside20'] += 1
                outcome_counts['offensiveTouchdowns'] += int(outcome['offensiveTouchdown'])
                if game == '2025_03_CIN_MIN':
                    sample = official_sample[outcome['offense']]
                    sample['possessions'] += 1
                    sample['touchdowns'] += int(outcome['offensiveTouchdown'])
    report = {'sourceSha256': source['sha256'], 'groups': len(groups),
              'adjudicationsApplied': len(adjudications['decisions']),
              'definition': 'Pre-snap field position strictly inside 20, ending at any touchdown; source row order preserved',
              'comparison': dict(counts), 'rejected': rejected,
              'ambiguousOwners': ambiguous, 'disagreements': disagreements,
              'outcomes': dict(outcome_counts), 'outcomeRejected': outcome_rejected,
              'cincinnatiMinnesotaSample': dict(official_sample),
              'publicationReady': False}
    (ROOT / 'reviews/red-zone-phase-reconciliation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__': main()
