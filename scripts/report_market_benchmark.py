"""Build a private reproducible benchmark report from an existing verified export."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from market_benchmark import grade_benchmark, digest, public_summary
from market_capture import load_export
from market_pairing import instant
from report_market_pairing import verify_protocol
from publish_market_summary import publish_summary

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export',required=True,type=Path)
    parser.add_argument('--schedule',type=Path,default=ROOT/'data/games.csv')
    parser.add_argument('--prepare-only',action='store_true',help='Retain candidate without replacing the displayed audit')
    args=parser.parse_args()
    now=datetime.now(timezone.utc)
    protocol=json.loads((ROOT/'reviews/market-pairing-protocol-publication.json').read_text())
    verify_protocol((ROOT/'reviews/market-pairing-protocol.md').read_bytes(),protocol,now)
    captures=load_export(args.export)
    manifest=json.loads((args.export/'manifest.json').read_text())
    if instant(manifest['exportedAt'])>now:raise ValueError('Export from future')
    inputs={name:(ROOT/'data'/name).read_bytes() for name in ('site.json','ledger.json','publications.json')}
    schedule=args.schedule.read_bytes()
    report=grade_benchmark(*(json.loads(inputs[name]) for name in ('site.json','ledger.json','publications.json')),
        captures,now,instant(manifest['startedAt']),schedule)
    report |= {'protocolHash':protocol['sha256'],'exportManifestHash':hashlib.sha256((args.export/'manifest.json').read_bytes()).hexdigest(),
        'captureHashes':[capture['sha256'] for capture in captures],
        'fileHashes':{name:hashlib.sha256(raw).hexdigest() for name,raw in inputs.items()},
        'codeHashes':{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in
            ('market_benchmark.py','report_market_benchmark.py','publish_market_summary.py','replay_market_benchmark.py','market_pairing.py','market_capture.py','report_market_pairing.py','personnel_schedule.py','publication.py','build_data.py','calibration.py')},
        'publicationStatus':'Private implementation evaluation; not yet a public benchmark or preregistration receipt'}
    folder=ROOT/'release-recovery/market-benchmark';folder.mkdir(parents=True,exist_ok=True)
    identity=digest(report)
    with (folder/(identity+'.json')).open('x') as output:
        json.dump(report,output,sort_keys=True,separators=(',',':'),allow_nan=False)
    # Preserve exact replay dependencies privately before emitting a shareable summary.
    dependencies={**{'data/'+name:raw for name,raw in inputs.items()},'data/games.csv':schedule,
        'export/manifest.json':(args.export/'manifest.json').read_bytes()}
    for name in report['codeHashes']:
        dependencies['scripts/'+name]=(ROOT/'scripts'/name).read_bytes().replace(b'\r\n',b'\n')
    for capture in manifest['captures']:
        name=capture['filename'] # load_export already validated the immutable filename.
        dependencies['export/'+name]=(args.export/name).read_bytes()
    retained=folder/identity
    for name,body in dependencies.items():
        target=retained/name;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as output:output.write(body)
    (retained/'inventory.json').write_text(json.dumps({name:hashlib.sha256(body).hexdigest() for name,body in dependencies.items()},sort_keys=True,indent=2)+'\n')
    summary=(public_summary(report)|{'publicationStatus':report['publicationStatus']}) if args.prepare_only else publish_summary(ROOT,identity)
    print(json.dumps(summary))


if __name__=='__main__':main()
