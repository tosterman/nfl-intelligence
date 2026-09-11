"""Read-only forecast replay followed by separate snapshot-bound total accounting."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import replay_forecast
import refresh
from total_explanation import decompose

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_ENGINE = '08495229d4ed0202c1abbe941005ca259d0dd190b6c7442206f24f52b1470ad9'


def build(root=ROOT):
    replay = replay_forecast.replay(root, new_only=True)
    if replay['mismatches'] or replay['unreplayable']:
        raise ValueError('Full current forecast replay did not pass')
    if replay['modelCodeHash'] != SUPPORTED_ENGINE:
        raise ValueError('Total accounting has not been reviewed for this engine')
    site = json.loads((root / 'data/site.json').read_bytes())
    expected_ids = {g['id'] for g in site['games'] if g.get('snapshot') and
                    g['snapshot'].get('generatedAt') == site['generatedAt']}
    matched_ids = {r['gameId'] for r in replay['records'] if r['status'] == 'matched'}
    if matched_ids != expected_ids or replay['matched'] != len(expected_ids):
        raise ValueError('New forecast coverage differs from replay')
    rows = refresh.base.load_rows(root / 'data/games.csv')
    statmap = {}
    for source in site['efficiencySources']:
        with (root / f"data/raw/stats_team_week_{source['season']}.csv").open(newline='', encoding='utf-8-sig') as stream:
            for row in csv.DictReader(stream):
                key = (row['game_id'], refresh.base.team(row['team']))
                if key in statmap:
                    raise ValueError('Duplicate efficiency input')
                statmap[key] = refresh.efficiency.rates(row)
    matched = {r['gameId'] for r in replay['records'] if r['status'] == 'matched'}
    games = {g['id']: g for g in site['games'] if g['id'] in matched}
    groups = {}
    for row in rows:
        if row['game_id'] in games:
            groups.setdefault((row['season'], row['week']), []).append(row)
    records = {}
    for targets in groups.values():
        ids = {r['game_id'] for r in targets}
        earlier = [r for r in rows if r['game_id'] not in ids and r['home_score'] is not None and r['away_score'] is not None]
        merged = sorted(earlier + targets, key=lambda r: (r['gameday'], r['game_id']))
        x, feature_rows = refresh.efficiency.features(merged, statmap, 90)
        weeks = {(r['season'], r['week'], r['game_type']) for r in targets}
        cutoff = min(r['gameday'] for r in merged if (r['season'], r['week'], r['game_type']) in weeks)
        train = np.array([r['gameday'] < cutoff and r['game_id'] not in ids and r['home_score'] is not None and r['away_score'] is not None for r in feature_rows])
        if int(train.sum()) < 500:
            raise ValueError('Insufficient feature history')
        y = np.array([[r['home_score'] - r['away_score'], r['home_score'] + r['away_score']] for r, ok in zip(feature_rows, train) if ok])
        efficiency_beta = refresh.efficiency.fit_symmetric(x[train], y, 10)
        score_cutoff = min(r['gameday'] for r in rows + targets if (r['season'], r['week'], r['game_type']) in weeks)
        score_beta, _, _ = refresh.base.fit(rows, score_cutoff, 180, 6)
        names = [f'{side} {name}' for side in ['offense', 'opponent allowed'] for name in refresh.efficiency.NAMES]
        for i, row in enumerate(feature_rows):
            if row['game_id'] not in ids:
                continue
            snapshot = games[row['game_id']]['snapshot']
            result = decompose(score_beta, efficiency_beta, x[i], refresh.base.IDX[row['home_team']], refresh.base.IDX[row['away_team']], names, snapshot['prediction']['total'])
            records[snapshot['hash']] = {**result, 'gameId': row['game_id'], 'snapshotHash': snapshot['hash'], 'cutoff': cutoff}
    if len(records) != len(matched):
        raise ValueError('Explanation coverage differs from replay')
    if hashlib.sha256((root / 'data/site.json').read_bytes()).hexdigest() != replay['siteSha256']:
        raise ValueError('Edition changed during explanatory replay')
    # Recheck source bytes after the secondary fits as well as before replay.
    if not replay_forecast.verify(root)['inputsMatch']:
        raise ValueError('Source bytes changed during explanatory replay')
    code_hash = hashlib.sha256(b''.join((ROOT / 'scripts' / name).read_bytes() for name in ['build_total_explanations.py', 'total_explanation.py'])).hexdigest()
    return {'schemaVersion': 1, 'siteSha256': replay['siteSha256'], 'modelCodeHash': replay['modelCodeHash'],
            'explanationCodeHash': code_hash, 'editionGeneratedAt': site['generatedAt'],
            'replayMatched': replay['matched'], 'records': records}


if __name__ == '__main__':
    result = build()
    # Review output only until immutable retention and UI selection are wired.
    (ROOT / 'reviews/total-explanations-replay.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'matchedForecasts': result['replayMatched'], 'explanations': len(result['records']), 'siteSha256': result['siteSha256']}), flush=True)
