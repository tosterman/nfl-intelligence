"""Rebuild the historical matchup artifact from pinned, retained source bytes."""
import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

try:
    from .explosive_plays import summarize
except ImportError:
    from explosive_plays import summarize


def build(manifest, root):
    def read_source(key):
        source = manifest[key]
        raw = (root / source['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != source['sha256']:
            raise ValueError(f'{key} digest mismatch')
        return csv.DictReader(io.StringIO(gzip.decompress(raw).decode('utf-8-sig')))

    schedule = list(read_source('schedule'))
    season = str(manifest['season'])
    selected = [g for g in schedule if g['game_id'].startswith(season + '_')]
    if not selected:
        raise ValueError('No schedule games for requested season')
    results = summarize(read_source('plays'), selected, manifest['cutoff'])
    expected = {(g['game_id'], team) for g in selected
                if g['gameday'] < manifest['cutoff']
                and all(g.get(k) not in ('', None, 'NA') for k in ('home_score', 'away_score'))
                for team in (g['home_team'], g['away_team'])}
    actual = {(r['gameId'], r['offense']) for r in results}
    if not expected or actual != expected:
        raise ValueError('Completed-game offense coverage is incomplete')
    teams = {}
    for row in results:
        for side, team in [('offense', row['offense']), ('defense', row['defense'])]:
            bucket = teams.setdefault(team, {'offense': {}, 'defense': {}})[side]
            for kind in ('passing', 'rushing'):
                counts = bucket.setdefault(kind, {'plays': 0, 'explosive': 0})
                for field in counts:
                    counts[field] += row[kind][field]
    return {'schemaVersion': 1, 'season': manifest['season'], 'cutoff': manifest['cutoff'],
            'definitions': {'passingYards': 20, 'rushingYards': 10,
                            'weighting': 'none', 'includesPostseason': True},
            'sourceManifestHash': hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest(),
            'games': results, 'teams': dict(sorted(teams.items()))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default='data/explosive-source.json')
    parser.add_argument('--output', default='data/explosive-plays.json')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = build(json.loads((root / args.manifest).read_text()), root)
    (root / args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(f"Verified {len(result['games'])} offense-game samples across {len(result['teams'])} teams")
