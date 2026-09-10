"""Exercise forecast generation in isolation; never publish staged artifacts."""
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from publication import context_matches, snapshot_valid

ROOT = Path(__file__).resolve().parents[1]


def main():
    recovery = ROOT / 'release-recovery'
    recovery.mkdir(exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix='context-builder-', dir=recovery))
    shutil.copytree(ROOT / 'scripts', staged / 'scripts', ignore=shutil.ignore_patterns('__pycache__'))
    (staged / 'data/raw').mkdir(parents=True)
    protected = ['ledger.json', 'publications.json', 'site.json', 'source.json', 'games.csv']
    original = {n: hashlib.sha256((ROOT / 'data' / n).read_bytes()).hexdigest() for n in protected}
    for name in ['ledger.json', 'publications.json']:
        shutil.copy2(ROOT / 'data' / name, staged / 'data' / name)
    for path in (ROOT / 'data/raw').glob('stats_team_week_*.csv'):
        shutil.copy2(path, staged / 'data/raw' / path.name)
    before = json.loads((staged / 'data/ledger.json').read_text())

    def run(offline):
        env = os.environ.copy()
        env['NFL_OFFLINE'] = '1' if offline else '0'
        result = subprocess.run([sys.executable, 'scripts/refresh.py'], cwd=staged, env=env,
                                check=True, capture_output=True, text=True)
        (staged / ('offline.log' if offline else 'acquisition.log')).write_text(result.stdout)
        return json.loads((staged / 'data/site.json').read_text()), json.loads((staged / 'data/ledger.json').read_text())

    site, first = run(False)
    assert first[:len(before)] == before, 'Existing ledger changed'
    added = first[len(before):]
    for name in ['games.csv', 'source.json', 'site.json', 'ledger.json']:
        shutil.copy2(staged / 'data' / name, staged / ('first-' + name))
    (staged / 'DIAGNOSTIC-ONLY.txt').write_text('Contains synthetic venue data from integration verification. Never publish this directory or treat it as a forecast receipt.\n')
    assert added and all(snapshot_valid(s) for s in added), 'Missing or invalid new snapshots'
    games = {g['id']: g for g in site['games']}
    assert all(context_matches(s, games[s['gameId']]) for s in added), 'Generated context mismatch'
    repeated, second = run(True)
    assert first == second, 'Identical run appended another forecast'

    # Deliberately synthetic venue edit: an unchanged score must still receive
    # a new context-bearing revision. This directory must never be deployed.
    target = added[0]['gameId']
    schedule = staged / 'data/games.csv'
    with schedule.open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream); fields = reader.fieldnames; rows = list(reader)
    for row in rows:
        if row['game_id'] == target:
            row['stadium'] = 'Synthetic verification venue - not a real schedule'
    with schedule.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    meta_path = staged / 'data/source.json'
    meta = json.loads(meta_path.read_text())
    meta.update(sha256=hashlib.sha256(schedule.read_bytes()).hexdigest(), url='fixture://context-builder/synthetic-venue', diagnosticOnly=True)
    meta_path.write_text(json.dumps(meta))
    changed, third = run(True)
    changes = third[len(second):]
    assert len(changes) == 1 and changes[0]['gameId'] == target, 'Venue-only change did not append exactly one revision'
    prior = next(s for s in added if s['gameId'] == target)
    assert changes[0]['prediction'] == prior['prediction'], 'Venue label unexpectedly altered scores'
    assert changes[0]['hash'] != prior['hash'], 'Changed context reused prior hash'
    changed_game = next(g for g in changed['games'] if g['id'] == target)
    assert context_matches(changes[0], changed_game) and not context_matches(prior, changed_game)
    assert changed_game['snapshot']['hash'] == changes[0]['hash'], 'Display selected old context'
    assert original == {n: hashlib.sha256((ROOT / 'data' / n).read_bytes()).hexdigest() for n in protected}, 'Workspace data changed'
    report = {'stagingDirectory': str(staged), 'diagnosticOnly': True, 'initialNewSnapshots':len(added),
              'unchangedRerunNewSnapshots':0, 'syntheticVenueChangeNewSnapshots':len(changes),
              'scoresUnchanged':True, 'originalLedgerPreserved':True, 'workspaceDataUnchanged':True,
              'generatedAt':site['generatedAt'], 'sourceHash':site['source']['sha256'],
              'workspaceHashes':original,
              'retainedInitialFiles': {n:hashlib.sha256((staged / ('first-' + n)).read_bytes()).hexdigest() for n in ['games.csv','source.json','site.json','ledger.json']},
              'verificationCodeHash':hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n', b'\n')).hexdigest()}
    (ROOT / 'reviews/context-builder-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
