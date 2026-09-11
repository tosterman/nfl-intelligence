"""Replay a local personnel candidate at its recorded calculation times."""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REVIEWS=('personnel-change-ledger.json','personnel-identity-audit.json','player-usage-audit.json',
         'player-registry-source.json','player-identity-source.csv.gz','player-usage-source.csv.gz')
STEPS=(('personnel_changes','data/personnel-changes.json',None,('reviews/personnel-change-ledger.json',)),
       ('audit_personnel_identity','reviews/personnel-identity-audit.json','generatedAt',()),
       ('audit_player_usage','reviews/player-usage-audit.json','generatedAt',()),
       ('build_public_usage','data/player-usage.json',None,()),
       ('build_season_participation','data/season-participation.json','calculatedAt',()))


def verify_output(actual,expected):
    def canonical(raw):
        return json.dumps(json.loads(raw),sort_keys=True,separators=(',',':'),allow_nan=False)
    if canonical(actual)!=canonical(expected):
        raise ValueError('Personnel replay output differs')


def candidate_files(root):
    files=list((root/'data').rglob('*.json'))+list((root/'data').rglob('*.csv'))+list((root/'data').rglob('*.gz'))
    files += [root/'reviews'/name for name in REVIEWS]
    files += list((root/'scripts').glob('*.py'))
    return {path.relative_to(root).as_posix():path.read_bytes() for path in sorted(set(files))}


CHILD = '''import importlib,sys
from pathlib import Path
from datetime import datetime
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'scripts'))
module=importlib.import_module(sys.argv[2])
at=datetime.fromisoformat(sys.argv[3]) if sys.argv[3] else None
if at:
 class FrozenDateTime(datetime):
  @classmethod
  def now(cls,tz=None):
   return at.astimezone(tz) if tz else at.replace(tzinfo=None)
 module.datetime=FrozenDateTime
if sys.argv[2]=='refresh_quarterbacks':
 import json
 from audit_personnel_identity import reconstruct
 from depth_chart import instant
 quarterback=json.loads((root/'data/quarterbacks.json').read_bytes())
 raw=reconstruct(root/'data/quarterback-sources',quarterback['sourceHash'])
 if module.normalize(raw,set(quarterback['teams']),instant(quarterback['retrievedAt']))!=quarterback['teams']:
  raise ValueError('Quarterback roles do not replay')
elif sys.argv[2]=='build_season_participation':
 module.write_receipts(root/'data/season-participation.json',module.build(root,at))
else:
 module.main()
'''


def replay(root):
    root=Path(root).resolve()
    original=candidate_files(root)
    parent=ROOT/'release-recovery';parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='personnel-replay-',dir=parent) as name:
        target=Path(name).resolve()
        if not target.is_relative_to(parent.resolve()):
            raise ValueError('Replay directory outside workspace')
        for relative,raw in original.items():
            path=target/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        qb_result=subprocess.run([sys.executable,'-c',CHILD,str(target),'refresh_quarterbacks',''],
                                 cwd=target,capture_output=True,timeout=180)
        if qb_result.returncode:
            (parent/'personnel-replay-failure.log').write_bytes(qb_result.stdout+qb_result.stderr)
            raise ValueError('Candidate quarterback replay failed')
        completed=[]
        for module,output,clock,other in STEPS:
            expected=original[output]
            at=json.loads(expected)[clock] if clock else ''
            result=subprocess.run([sys.executable,'-c',CHILD,str(target),module,at],
                                  cwd=target,capture_output=True,timeout=180)
            if result.returncode:
                (parent/'personnel-replay-failure.log').write_bytes(result.stdout+result.stderr)
                raise ValueError(f'Personnel replay failed: {module}')
            for relative in (output,*other):
                verify_output((target/relative).read_bytes(),original[relative])
                # Preserve the verified original metadata transport for downstream
                # exact audit hashes (Windows and Git use different line endings).
                (target/relative).write_bytes(original[relative])
            completed.append(module)
            print(f'Replayed {module}',flush=True)
    if candidate_files(root)!=original:
        raise ValueError('Candidate changed during replay')
    return {'steps':completed,'files':{name:{'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
                                    for name,raw in original.items()},'inputsUnchanged':True,'quarterbackRolesReplayed':True}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    args=parser.parse_args()
    report=replay(args.root)
    (ROOT/'reviews/personnel-candidate-replay.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'steps':report['steps'],'files':len(report['files']),'inputsUnchanged':True}))
