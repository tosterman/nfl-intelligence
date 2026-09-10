"""Describe role disagreements; never infer a starter from outcome labels."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from depth_chart import instant, quarterbacks_before

ROOT = Path(__file__).resolve().parents[1]


def main():
    audit_path = ROOT / 'reviews/quarterback-role-evaluation.json'
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    source_path = ROOT / 'release-recovery/depth_charts_2025.csv'
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if source_hash != audit['depthSourceHash']:
        raise ValueError('Role audit and source bytes differ')
    observations = audit['observations']
    keys = {(r['gameId'], r['team'], r['hoursBeforeKickoff']) for r in observations}
    if len(keys) != len(observations):
        raise ValueError('Duplicate role observations')
    # Retain all positions at each selected timestamp, including missing QB rows.
    wanted = {(r['team'], instant(r['chartRecordedAt'])) for r in observations if r['chartRecordedAt']}
    snapshots = defaultdict(list)
    with source_path.open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            key = (row['team'], instant(row['dt']))
            if key in wanted:
                snapshots[key].append(row)
    records = []
    for observation in observations:
        team = observation['team']
        at = observation['chartRecordedAt']
        rows = snapshots[(team, instant(at))] if at else []
        selected = quarterbacks_before(rows, {team}, instant(observation['cutoff']), audit['maximumChartAgeHours'])[team]
        game_qb = observation['gameQb']
        status = ('missing_game_qb' if not game_qb else 'unavailable_chart' if selected['status'] != 'available'
                  else 'match' if selected['listedFirst'] == game_qb else 'different')
        if selected['listedFirst'] != observation['listedFirst'] or status != observation['result']:
            raise ValueError('Cannot reproduce original role observation')
        ranks = sorted({p['rank'] for p in selected['quarterbacks'] if p['playerId'] == game_qb})
        category = status if status != 'different' else ('listed_lower' if ranks else 'absent_from_chart')
        records.append(observation | {'category': category, 'recordedGameQbRanks': ranks,
                                      'listedQuarterbacks': selected['quarterbacks']})
    by_game = defaultdict(dict)
    for row in records:
        by_game[(row['gameId'], row['team'])][row['hoursBeforeKickoff']] = row
    if any(set(pair) != {24, 0} for pair in by_game.values()):
        raise ValueError('Expected paired cutoffs for every team-game')
    transitions = Counter((pair[24]['category'], pair[0]['category']) for pair in by_game.values())
    summaries = {}
    for hours in (24, 0):
        subset = [r for r in records if r['hoursBeforeKickoff'] == hours]
        summaries[str(hours)] = {
            'teamGames': len(subset),
            'categories': dict(Counter(r['category'] for r in subset)),
            'disagreementRanks': dict(Counter(','.join(map(str, r['recordedGameQbRanks'])) or 'absent'
                                              for r in subset if r['result'] == 'different')),
        }
    output = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'depthSourceHash': source_hash,
        'roleAuditHash': hashlib.sha256(audit_path.read_bytes()).hexdigest(),
        'scheduleHash': audit['scheduleHash'],
        'codeHashes': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                       for p in ('scripts/audit_quarterback_disagreements.py', 'scripts/depth_chart.py')},
        'summaries': summaries,
        'pairedTransitions': [{'from24Hours': a, 'toKickoff': b, 'count': n}
                              for (a, b), n in sorted(transitions.items())],
        'records': records,
        'limitations': 'Descriptive analysis of previously examined 2025 data, not a new holdout. '
                      'Schedule QB labels are retrospective and do not establish snap shares or announcement timing. '
                      'Listed alternatives are not calibrated scenario probabilities. Historical files may contain corrections.',
    }
    (ROOT / 'reviews/quarterback-disagreements.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: output[k] for k in ('summaries', 'pairedTransitions')}, indent=2))


if __name__ == '__main__':
    main()
