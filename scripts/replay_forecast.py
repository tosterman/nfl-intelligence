"""Read-only numerical replay of supported current snapshots from retained inputs.

Uses the existing inference functions without calling acquisition or publication.
Does not reproduce prior revisions whose input bytes are absent from this bundle.
"""
import csv
import hashlib
import json
import math
from numbers import Real
from datetime import datetime
from pathlib import Path

import refresh
from publication import context_matches, snapshot_valid
from verify_forecast_inputs import verify

ROOT = Path(__file__).resolve().parents[1]


def exact_value(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return False
    if isinstance(left, Real) and isinstance(right, Real):
        return math.isfinite(left) and math.isfinite(right) and left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(exact_value(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(exact_value(a, b) for a, b in zip(left, right))
    return left == right


def compare_prediction(snapshot, prediction, training_games, training_through):
    # Compare the complete rounded publication object, including field presence,
    # profiles and contributions. No tolerance hides a displayed-number change.
    return (exact_value(snapshot['prediction'], prediction)
            and type(snapshot['trainingGames']) is int and snapshot['trainingGames'] == training_games
            and snapshot['trainingThrough'] == training_through)


def replay(root=ROOT):
    root = Path(root)
    inputs = verify(root)
    if not inputs['inputsMatch']:
        raise ValueError('Missing or mismatched retained inputs')
    raw = (root / 'data/site.json').read_bytes()
    site = json.loads(raw)
    if site['modelVersion'] != refresh.VERSION or site['model']['configuration'] != refresh.CONFIG:
        raise ValueError('Unsupported edition model or configuration')
    code_hash = hashlib.sha256(b''.join(
        (ROOT / 'scripts' / name).read_text().replace('\r\n', '\n').encode()
        for name in ['build_data.py', 'experiment_model.py', 'refresh.py'])).hexdigest()
    rows = refresh.base.load_rows(root / 'data/games.csv')
    refresh.validate_schedule(rows)
    by_id = {r['game_id']: r for r in rows}
    source_hashes = [s['sha256'] for s in site['efficiencySources']]
    statmap = {}
    for source in site['efficiencySources']:
        with (root / f"data/raw/stats_team_week_{source['season']}.csv").open(newline='', encoding='utf-8-sig') as stream:
            for r in csv.DictReader(stream):
                key = (r['game_id'], refresh.base.team(r['team']))
                if key in statmap:
                    raise ValueError('Duplicate efficiency game/team')
                statmap[key] = refresh.efficiency.rates(r)
    results = []
    groups = {}
    seen = set()
    for game in site['games']:
        if game['id'] in seen:
            raise ValueError('Duplicate edition game')
        seen.add(game['id'])
        snapshot = game.get('snapshot')
        if not snapshot:
            continue
        result = {'gameId': game['id'], 'snapshotHash': snapshot.get('hash')}
        if not snapshot_valid(snapshot):
            raise ValueError('Invalid snapshot hash')
        if (snapshot.get('modelCodeHash') != code_hash or snapshot.get('configuration') != refresh.CONFIG
                or snapshot.get('modelVersion') != refresh.VERSION
                or snapshot.get('sourceHash') != site['source']['sha256']
                or snapshot.get('efficiencySourceHashes') != source_hashes):
            results.append(result | {'status': 'unreplayable', 'reason': 'Retained inputs or running engine do not match this revision'})
            continue
        row = by_id.get(game['id'])
        if not row or not row['gametime']:
            raise ValueError('Snapshot schedule row missing')
        context = {'season': row['season'], 'week': row['week'], 'type': row['game_type'],
                   'home': row['home_team'], 'away': row['away_team'],
                   'kickoff': refresh.base.kickoff(row).isoformat(), 'venue': row['stadium'],
                   'neutral': row['location'] == 'Neutral'}
        if snapshot.get('gameId') != game['id'] or not context_matches(snapshot, context) or not context_matches(snapshot, game):
            raise ValueError('Incompatible game context')
        generated = datetime.fromisoformat(snapshot['generatedAt'])
        if generated.tzinfo is None or generated >= refresh.base.kickoff(row):
            raise ValueError('Invalid pregame generation time')
        groups.setdefault((row['season'], row['week']), []).append((row, snapshot, result))
    if not groups:
        raise ValueError('No current snapshots can be replayed with retained evidence')
    _, sigmas = refresh.replay_blend(rows, statmap)
    for (season, week), group in groups.items():
        cutoff = min(r['gameday'] for r in rows if r['season'] == season and r['week'] == week)
        predictions = refresh.efficiency.infer_blend(rows, statmap, [r for r, _, _ in group])
        _, n, last = refresh.base.fit(rows, cutoff, 180, 6)
        for row, snapshot, result in group:
            blend = predictions[row['game_id']]
            prediction = refresh.canonical_prediction(blend['homeMargin'], blend['total'], sigmas,
                refresh.evidence(blend), refresh.profiles_for(row, statmap, rows, cutoff))
            matches = compare_prediction(snapshot, prediction, n, last)
            results.append(result | {'status': 'matched' if matches else 'mismatch',
                                    'weeklyCutoff': cutoff, 'recomputedPredictionHash': refresh.digest(prediction)})
    return {'editionGeneratedAt': site['generatedAt'], 'siteSha256': hashlib.sha256(raw).hexdigest(),
            'modelCodeHash': code_hash, 'inputFiles': len(inputs['files']),
            'matched': sum(r['status'] == 'matched' for r in results),
            'mismatches': sum(r['status'] == 'mismatch' for r in results),
            'unreplayable': sum(r['status'] == 'unreplayable' for r in results),
            'comparison': 'Exact equality of full rounded prediction objects and training metadata; no numerical tolerance.',
            'scope': 'Current snapshots only. Numerical reproducibility is not vintage-data, publication or predictive-accuracy evidence.',
            'records': results}


if __name__ == '__main__':
    report = replay()
    print(json.dumps(report, indent=2))
    if report['mismatches']:
        raise SystemExit(1)
    if report['unreplayable']:
        raise SystemExit(2)
