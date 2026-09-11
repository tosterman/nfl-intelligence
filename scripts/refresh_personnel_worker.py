"""Refresh an isolated restored worker; never publishes to storage."""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime,timezone
from pathlib import Path
from personnel_presentation import assemble,FILES

ROOT=Path(__file__).resolve().parents[1]
COLLECTORS=(('refresh_personnel.py','personnel.json','personnel-collection.json','unavailable'),
            ('refresh_quarterbacks.py','quarterbacks.json','quarterback-collection.json','unavailable'),
            ('refresh_participation.py','participation-source.json','participation-collection.json','failed'))
DERIVATIONS=(('audit_personnel_identity.py','identity-audit'),('audit_player_usage.py','historical-usage'),
             ('build_public_usage.py','historical-usage'),('build_season_participation.py','current-participation'))
DERIVED_FILES=('reviews/personnel-identity-audit.json','reviews/player-usage-audit.json',
               'data/player-usage.json','data/season-participation.json')


def run(root,script):
    try:
        result=subprocess.run([sys.executable,str(root/'scripts'/script)],cwd=root,capture_output=True,timeout=240)
        (root/'reviews'/(script+'.log')).write_bytes(result.stdout+result.stderr)
        return result.returncode
    except subprocess.TimeoutExpired:
        (root/'reviews'/(script+'.log')).write_text('Worker step timed out\n')
        return 124


def collect(root,runner=run):
    results=[]
    for script,pointer,state,failure in COLLECTORS:
        before=(root/'data'/pointer).read_bytes()
        started=datetime.now(timezone.utc).isoformat()
        code=runner(root,script)
        if code:
            # A timeout may interrupt a collector between its pointer/state writes.
            (root/'data'/pointer).write_bytes(before)
            value={'status':failure,'checkedAt':started} if failure=='unavailable' else {
                'status':failure,'attemptedAt':started,'season':json.loads(before)['season']}
            (root/'data'/state).write_text(json.dumps(value,indent=2)+'\n')
        results.append({'step':script,'exitCode':code})
    return results


def derive(root,runner=run):
    original={name:(root/name).read_bytes() for name in DERIVED_FILES}
    results=[]
    for script,failure in DERIVATIONS:
        code=runner(root,script);results.append({'step':script,'exitCode':code})
        if code:
            for name,raw in original.items():(root/name).write_bytes(raw)
            return failure,results
    return None,results


def replay_sources(worker,previous_capture):
    code='''import sys,json,hashlib
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'scripts'))
from personnel_transition import build_transition
from personnel_changes import load_capture
from audit_personnel_identity import reconstruct
from refresh_quarterbacks import normalize
from depth_chart import instant
p=json.loads((root/'data/personnel.json').read_bytes())
q=json.loads((root/'data/quarterbacks.json').read_bytes())
current=hashlib.sha256((json.dumps(p,sort_keys=True,separators=(',',':'))+'\\n').encode()).hexdigest()
capture=load_capture(root/'data/personnel-sources'/(current+'.snapshot.json.gz'),root/'data/personnel-sources')
if not all(capture[k]==v for k,v in p.items()):raise ValueError('Personnel capture differs')
if normalize(reconstruct(root/'data/quarterback-sources',q['sourceHash']),set(q['teams']),instant(q['retrievedAt']))!=q['teams']:
 raise ValueError('Quarterback roles do not replay')
if current!=sys.argv[2]:
 transition=build_transition(root/'data/personnel-sources',current,sys.argv[2])
 (root/'data/personnel-changes.json').write_text(json.dumps(transition['presentation'],indent=2)+'\\n')
 (root/'reviews/personnel-runtime-transition.json').write_text(json.dumps(transition,indent=2)+'\\n')
'''
    replay=subprocess.run([sys.executable,'-c',code,str(worker),previous_capture],cwd=worker,capture_output=True,timeout=240)
    (worker/'reviews/source-replay.log').write_bytes(replay.stdout+replay.stderr)
    if replay.returncode:raise ValueError('Refreshed source replay failed; candidate not assembled')


def main(restored,acquire=False):
    restored=restored.resolve()
    receipt=json.loads((restored/'accepted-publication.json').read_bytes())
    parent=ROOT/'release-recovery';parent.mkdir(exist_ok=True)
    worker=Path(tempfile.mkdtemp(prefix='personnel-refresh-',dir=parent))
    for name in ('data','reviews','scripts'):shutil.copytree(restored/name,worker/name)
    # Record the new orchestrator; accepted source-processing scripts stay pinned.
    for name in ('refresh_personnel_worker.py','personnel_presentation.py','personnel_transition.py'):
        shutil.copyfile(ROOT/'scripts'/name,worker/'scripts'/name)
    before=(worker/'data/personnel.json').read_bytes()
    acquisitions=collect(worker) if acquire else []
    replay_sources(worker,receipt['capture'])
    failure,steps=derive(worker)
    files={name:(worker/'data'/name).read_bytes() for name in (*FILES,'games.csv')}
    files['identityAudit']=(worker/'reviews/personnel-identity-audit.json').read_bytes()
    presentation=assemble(files,derivation_failure=failure)
    (worker/'personnel-presentation.json').write_text(json.dumps(presentation,sort_keys=True,separators=(',',':'))+'\n')
    report={'checkedAt':datetime.now(timezone.utc).isoformat(),'previousPublication':receipt['publication'],
        'previousCapture':receipt['capture'],'acquisitions':acquisitions,'derivations':steps,'derivationFailure':failure,
        'sourceReplay':True,'personnelChanged':before!=(worker/'data/personnel.json').read_bytes(),
        'directory':worker.relative_to(ROOT).as_posix(),'reports':len(presentation['evidence']['snapshot']['players']),
        'scope':'Isolated refresh candidate only; no independent derived replay or storage publication'}
    (worker/'refresh-report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'reviews/personnel-runtime-refresh.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('restored',type=Path)
    parser.add_argument('--collect',action='store_true')
    args=parser.parse_args();main(args.restored,args.collect)
