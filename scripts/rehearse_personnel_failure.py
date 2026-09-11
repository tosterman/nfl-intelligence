"""Simulate failed feeds and derivation in a local package; never publish."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime,timezone
from refresh_personnel_worker import collect,derive
from replay_personnel_candidate import replay
from personnel_incremental_archive import build
from personnel_archive import encode

ROOT=Path(__file__).resolve().parents[1]

def main(restored):
    receipt=json.loads((restored/'accepted-publication.json').read_bytes())
    worker=Path(tempfile.mkdtemp(prefix='personnel-failure-test-',dir=ROOT/'release-recovery'))
    for folder in ('data','reviews','scripts'):shutil.copytree(restored/folder,worker/folder)
    acquisitions=collect(worker,lambda *_:124)
    failure,steps=derive(worker,lambda *_:124)
    report={'simulation':True,'checkedAt':datetime.now(timezone.utc).isoformat(),
        'previousPublication':receipt['publication'],'previousCapture':receipt['capture'],
        'acquisitions':acquisitions,'derivations':steps,'derivationFailure':failure}
    (worker/'refresh-report.json').write_bytes(encode(report))
    proof=replay(worker,True)
    result=build(worker,proof)
    selected=json.loads(result['objects'][result['publication']['sha256']])
    presentation=json.loads(result['objects'][selected['presentation']['sha256']])
    if presentation['evidence']['current'] is not None or presentation['evidence']['historical'] is not None:
        raise ValueError('Simulated failure exposed derived usage')
    for name,key in [('personnel.json','snapshot'),('quarterbacks.json','quarterback')]:
        if json.loads((restored/'data'/name).read_bytes())!=presentation['evidence'][key]:
            raise ValueError('Simulated failure changed source dates or records')
    package=worker/'package';package.mkdir()
    for identity,raw in result['objects'].items():(package/identity).write_bytes(raw)
    (package/'candidate.json').write_bytes(encode({**result,'objects':list(result['objects'])}))
    summary={'simulation':True,'directory':worker.relative_to(ROOT).as_posix(),
        'publication':result['publication'],'previousPublication':receipt['publication'],
        'sourceReplay':True,'derivedStepsReplayed':proof['steps'],'derivedUsageWithheld':True,
        'sourceDatesPreserved':True,'scope':'Local simulated outage; not actual feed status or storage publication'}
    (ROOT/'reviews/personnel-failure-rehearsal.json').write_bytes(encode(summary))
    print(json.dumps(summary))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('restored',type=Path)
    main(parser.parse_args().restored)
