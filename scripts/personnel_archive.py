"""Package the fully replayed initial personnel archive; no storage writes."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from replay_personnel_candidate import candidate_files,STEPS
from personnel_presentation import assemble,FILES

ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()


def verify_inventory(files,inventory):
    if set(files)!=set(inventory):raise ValueError('Replay inventory scope differs')
    for name,raw in files.items():
        if (len(name)>240 or not re.fullmatch(r'(data|reviews|scripts)/[a-zA-Z0-9_./-]+',name)
                or any(not part or part.startswith('.') for part in name.split('/'))):
            raise ValueError('Unsafe personnel archive path')
        if not 0<len(raw)<=10_000_000 or inventory[name]!={'sha256':sha(raw),'bytes':len(raw)}:
            raise ValueError('Replay inventory bytes differ')


def build(root,proof):
    if (proof.get('steps')!=[step[0] for step in STEPS] or proof.get('inputsUnchanged') is not True
            or proof.get('quarterbackRolesReplayed') is not True):
        raise ValueError('Complete personnel replay required')
    files=candidate_files(root)
    verify_inventory(files,proof['files'])
    inputs={name:files['data/'+name] for name in (*FILES,'games.csv')}
    inputs['identityAudit']=files['reviews/personnel-identity-audit.json']
    presentation=assemble(inputs)
    archive_files={**files,'reviews/personnel-replay-proof.json':encode(proof)}
    for name in ('replay_personnel_candidate.py','personnel_archive.py','personnel_presentation.py','personnel_schedule.py'):
        key='scripts/'+name;raw=(ROOT/key).read_bytes()
        if key in archive_files and archive_files[key]!=raw:
            raise ValueError('Packaging code differs from retained inputs')
        archive_files[key]=raw
    objects={}
    def retain(raw):
        identity=sha(raw);objects[identity]=raw;return {'sha256':identity,'bytes':len(raw)}
    archive={name:retain(raw) for name,raw in sorted(archive_files.items())}
    selected=retain(encode(presentation))
    publication=retain(encode({'schemaVersion':1,'kind':'personnel-publication',
        'generatedAt':presentation['generatedAt'],'presentation':selected,'archive':archive,'previous':None}))
    if (len(objects)>5002 or len(archive)>5000 or sum(map(len,objects.values()))>64_000_000
            or publication['bytes']>1_000_000 or selected['bytes']>2_000_000):
        raise ValueError('Personnel bootstrap archive exceeds capacity bounds')
    if candidate_files(root)!=files:raise ValueError('Candidate changed during packaging')
    return {'publication':publication,'objects':objects,'summary':{
        'generatedAt':presentation['generatedAt'],'archiveFiles':len(archive),'objectCount':len(objects),
        'bytes':sum(map(len,objects.values())),'presentationBytes':selected['bytes'],
        'reports':len(presentation['evidence']['snapshot']['players'])}}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('--proof',type=Path,default=ROOT/'reviews/personnel-candidate-replay.json')
    args=parser.parse_args()
    result=build(args.root,json.loads(args.proof.read_bytes()))
    output=ROOT/'release-recovery/personnel-bootstrap'/result['publication']['sha256']
    output.mkdir(parents=True,exist_ok=True)
    for identity,raw in result['objects'].items():
        path=output/identity
        if path.exists() and path.read_bytes()!=raw:raise ValueError('Candidate object conflict')
        path.write_bytes(raw)
    manifest={'publication':result['publication'],'objects':list(result['objects']),**result['summary']}
    (output/'candidate.json').write_bytes(encode(manifest))
    report={**manifest,'directory':output.relative_to(ROOT).as_posix(),'scope':'Initial archive package only; no storage or site publication'}
    (ROOT/'reviews/personnel-bootstrap-package.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='objects'}))
