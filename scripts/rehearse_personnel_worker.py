"""Offline worker rehearsal using retained sources; never publishes or collects."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from audit_personnel_identity import reconstruct
from refresh_quarterbacks import normalize
from depth_chart import instant
from personnel_schedule import verify_schedule
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ('site.json', 'games.csv', 'personnel.json', 'personnel-collection.json',
        'quarterbacks.json', 'quarterback-collection.json', 'participation-source.json',
        'participation-collection.json')
SOURCES = ('personnel-sources', 'quarterback-sources', 'participation-sources')
REVIEWS = ('player-usage-source.csv.gz', 'player-identity-source.csv.gz', 'player-registry-source.json')
STEPS = ('personnel_changes.py', 'audit_personnel_identity.py', 'audit_player_usage.py',
         'build_public_usage.py', 'build_season_participation.py')


def main():
    parent = ROOT / 'release-recovery'
    parent.mkdir(exist_ok=True)
    worker = Path(tempfile.mkdtemp(prefix='personnel-worker-', dir=parent))
    for folder in ('data', 'reviews', 'scripts'):
        (worker / folder).mkdir()
    for path in (ROOT / 'scripts').glob('*.py'):
        shutil.copyfile(path, worker / 'scripts' / path.name)
    for name in DATA:
        shutil.copyfile(ROOT / 'data' / name, worker / 'data' / name)
    for name in SOURCES:
        shutil.copytree(ROOT / 'data' / name, worker / 'data' / name)
    for name in REVIEWS:
        shutil.copyfile(ROOT / 'reviews' / name, worker / 'reviews' / name)
    files = sorted(path for path in worker.rglob('*') if path.is_file())
    inputs = {path.relative_to(worker).as_posix(): {
        'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()
    } for path in files}
    contexts = verify_schedule(json.loads((worker / 'data/site.json').read_bytes()),
                               (worker / 'data/games.csv').read_bytes())
    quarterback = json.loads((worker / 'data/quarterbacks.json').read_bytes())
    raw = reconstruct(worker / 'data/quarterback-sources', quarterback['sourceHash'])
    if normalize(raw, set(quarterback['teams']), instant(quarterback['retrievedAt'])) != quarterback['teams']:
        raise ValueError('Quarterback roles do not replay from retained source')
    completed = []
    for step in STEPS:
        run = subprocess.run([sys.executable, str(worker / 'scripts' / step)], cwd=worker,
                             capture_output=True, timeout=180)
        (worker / 'reviews' / (step + '.log')).write_bytes(run.stdout + run.stderr)
        if run.returncode:
            raise RuntimeError(f'{step} failed; retained log in {worker}')
        completed.append(step)
    outputs = {}
    for name in ('personnel-changes.json', 'player-usage.json', 'season-participation.json'):
        path = worker / 'data' / name
        value = json.loads(path.read_bytes())
        outputs[name] = {'bytes': path.stat().st_size,
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'records': len(value.get('records', value.get('changes', [])))}
    unchanged = all(hashlib.sha256((worker / name).read_bytes()).hexdigest() == meta['sha256']
                    for name, meta in inputs.items())
    if not unchanged:
        raise ValueError('Rehearsal changed copied input evidence')
    report = {'checkedAt': datetime.now(timezone.utc).isoformat(),
              'scope': 'Offline isolated reconstruction from retained sources; no collection or publication',
              'steps': completed, 'inputsUnchanged': unchanged,
              'quarterbackRolesReplayed': True,
              'scheduleContextsVerified': len(contexts),
              'inputFiles': len(inputs), 'inputBytes': sum(v['bytes'] for v in inputs.values()),
              'outputs': outputs, 'inputs': inputs}
    target = ROOT / 'reviews/personnel-worker-rehearsal.json'
    target.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'inputs'}))


if __name__ == '__main__':
    main()
