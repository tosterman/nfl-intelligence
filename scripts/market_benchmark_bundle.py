"""Bounded, hash-verified private benchmark packages; restore never executes code."""
import argparse
import base64
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
from replay_market_benchmark import replay

MAX_BYTES=20_000_000
MAX_EXPANDED=64_000_000


def safe_name(name):
    return name=='report.json' or name=='inventory.json' or bool(re.fullmatch(
        r'(data/[a-z-]+\.(json|csv)|scripts/[a-z_]+\.py|export/(manifest\.json|[a-f0-9]{64}\.json\.gz))',name))


def decode(body):
    if len(body)>MAX_BYTES:raise ValueError('Benchmark bundle too large')
    with gzip.GzipFile(fileobj=io.BytesIO(body)) as stream:raw=stream.read(MAX_EXPANDED+1)
    if len(raw)>MAX_EXPANDED:raise ValueError('Expanded benchmark bundle too large')
    package=json.loads(raw)
    if package.get('schemaVersion')!=1 or package.get('kind')!='market-benchmark' or not isinstance(package.get('files'),dict) or not 1<=len(package['files'])<=1000:
        raise ValueError('Invalid benchmark package')
    files={}
    for name,entry in package['files'].items():
        if not safe_name(name):raise ValueError('Unsafe benchmark path')
        value=base64.b64decode(entry['base64'],validate=True)
        if hashlib.sha256(value).hexdigest()!=entry['sha256']:raise ValueError('Benchmark file hash differs')
        files[name]=value
    identity=hashlib.sha256(files.get('report.json',b'')).hexdigest()
    if package.get('reportHash')!=identity or 'report.json' not in files:raise ValueError('Benchmark report hash differs')
    return identity,files


def package(identity,folder):
    proof=replay(identity,folder)
    if proof.get('matched') is not True:raise ValueError('Unreplayed benchmark')
    files={'report.json':(folder/(identity+'.json')).read_bytes()}
    retained=folder/identity
    inventory=json.loads((retained/'inventory.json').read_text())
    for name in [*inventory,'inventory.json']:
        if not safe_name(name):raise ValueError('Unexpected benchmark dependency')
        path=retained/name
        if path.is_symlink():raise ValueError('Benchmark symlink forbidden')
        raw=path.read_bytes()
        if name in inventory and hashlib.sha256(raw).hexdigest()!=inventory[name]:raise ValueError('Retained dependency changed')
        files[name]=raw
    envelope={'schemaVersion':1,'kind':'market-benchmark','reportHash':identity,
        'files':{name:{'sha256':hashlib.sha256(raw).hexdigest(),'base64':base64.b64encode(raw).decode()} for name,raw in files.items()}}
    body=gzip.compress(json.dumps(envelope,sort_keys=True,separators=(',',':')).encode(),mtime=0)
    decode(body)
    return body


def restore(body,target):
    identity,files=decode(body)
    if target.exists():raise ValueError('Restore destination must not exist')
    # All paths and bytes are validated before creating any output.
    target.mkdir(parents=True)
    for name,raw in files.items():
        path=target/(identity+'.json') if name=='report.json' else target/identity/name
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as output:output.write(raw)
    return identity


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('identity')
    parser.add_argument('--folder',type=Path,default=Path(__file__).resolve().parents[1]/'release-recovery/market-benchmark')
    args=parser.parse_args()
    body=package(args.identity,args.folder)
    sha=hashlib.sha256(body).hexdigest();path=args.folder/(sha+'.bundle.json.gz')
    if path.exists():
        if path.read_bytes()!=body:raise ValueError('Existing bundle differs')
    else:
        with path.open('xb') as output:output.write(body)
    print(json.dumps({'reportHash':args.identity,'sha256':sha,'bytes':len(body),'path':str(path)}))
