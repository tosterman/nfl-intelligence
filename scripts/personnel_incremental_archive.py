"""Package a replayed refresh linked to its accepted predecessor; no writes to storage."""
import argparse
import hashlib
import json
from pathlib import Path
from replay_personnel_candidate import candidate_files,STEPS,validate_degraded_report
from personnel_archive import verify_inventory,encode
from personnel_presentation import assemble,FILES

ROOT=Path(__file__).resolve().parents[1]


def build(root,proof):
    failure=proof.get('derivationFailure')
    if (proof.get('mode')!='recurring' or proof.get('steps')!=([] if failure else [s[0] for s in STEPS[1:]])
            or any(proof.get(key) is not True for key in ('inputsUnchanged','quarterbackRolesReplayed','transitionReplayed'))):
        raise ValueError('Complete recurring replay required')
    if set(proof.get('checkerHashes',{}))!={'replay_personnel_candidate.py','refresh_personnel_worker.py'}:
        raise ValueError('Complete replay checker identities required')
    files=candidate_files(root,True);verify_inventory(files,proof['files'])
    report=json.loads(files['reviews/personnel-refresh-report.json'])
    if failure:
        if validate_degraded_report(report)!=failure or proof.get('derivedUsageWithheld') is not True:
            raise ValueError('Degraded publication evidence differs')
    if (report['previousPublication']!=proof['previousPublication'] or report['previousCapture']!=proof['previousCapture']
            or report['derivationFailure']!=failure):raise ValueError('Refresh predecessor differs')
    inputs={name:files['data/'+name] for name in (*FILES,'games.csv')}
    inputs['identityAudit']=files['reviews/personnel-identity-audit.json']
    presentation=assemble(inputs,derivation_failure=failure)
    retained={**files,'reviews/personnel-replay-proof.json':encode(proof)}
    for name in ('replay_personnel_candidate.py','refresh_personnel_worker.py','personnel_incremental_archive.py','personnel_presentation.py','personnel_archive.py'):
        raw=(ROOT/'scripts'/name).read_bytes()
        if name in proof['checkerHashes'] and hashlib.sha256(raw).hexdigest()!=proof['checkerHashes'][name]:
            raise ValueError('Replay checker changed after proof')
        # Keep producer code intact and retain current verification/packaging code separately.
        retained['reviews/checkers/'+name]=raw
    objects={}
    def retain(raw):
        identity=hashlib.sha256(raw).hexdigest();objects[identity]=raw
        return {'sha256':identity,'bytes':len(raw)}
    archive={name:retain(raw) for name,raw in sorted(retained.items())}
    selected=retain(encode(presentation))
    publication=retain(encode({'schemaVersion':1,'kind':'personnel-publication','generatedAt':presentation['generatedAt'],
        'presentation':selected,'archive':archive,'previous':proof['previousPublication']}))
    total=sum(map(len,objects.values()))
    if len(objects)>5002 or len(archive)>5000 or total>64_000_000 or publication['bytes']>1_000_000:
        raise ValueError('Personnel refresh exceeds capacity')
    if candidate_files(root,True)!=files:raise ValueError('Refresh changed during packaging')
    return {'publication':publication,'objects':objects,'objectCount':len(objects),'bytes':total,
            'previousPublication':proof['previousPublication'],'previousCapture':proof['previousCapture']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    args=parser.parse_args()
    result=build(args.root,json.loads((ROOT/'reviews/personnel-refresh-replay.json').read_bytes()))
    output=ROOT/'release-recovery/personnel-incremental'/result['publication']['sha256'];output.mkdir(parents=True,exist_ok=True)
    for identity,raw in result['objects'].items():
        path=output/identity
        if path.exists() and path.read_bytes()!=raw:raise ValueError('Immutable package conflict')
        path.write_bytes(raw)
    manifest={**result,'objects':list(result['objects'])}
    (output/'candidate.json').write_bytes(encode(manifest))
    report={**manifest,'directory':output.relative_to(ROOT).as_posix(),'scope':'Replay-verified incremental package; not published'}
    (ROOT/'reviews/personnel-incremental-package.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='objects'}))
