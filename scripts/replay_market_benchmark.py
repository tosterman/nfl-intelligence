"""Replay a locally retained benchmark using its pinned code and source bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

CHILD='''import json, socket, sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'scripts')
from market_benchmark import grade_benchmark
from market_capture import load_export
from market_pairing import instant
report=json.loads(Path('../'+Path.cwd().name+'.json').read_text())
inputs=[json.loads(Path('data/'+name).read_text()) for name in ['site.json','ledger.json','publications.json']]
with patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')):
 result=grade_benchmark(*inputs,load_export(Path('export')),instant(report['checkedAt']),instant(report['coverageThrough']),Path('data/games.csv').read_bytes())
if any(report.get(key)!=value for key,value in result.items()):raise ValueError('Benchmark replay differs')
print(json.dumps({'reportHash':Path.cwd().name,'pairedGameCount':result['pairedGameCount'],'networkBlocked':True,'matched':True}))
'''


def replay(identity,folder):
    if not re.fullmatch('[a-f0-9]{64}',identity):raise ValueError('Invalid report identity')
    raw=(folder/(identity+'.json')).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=identity:raise ValueError('Report hash differs')
    report=json.loads(raw);retained=folder/identity
    expected={**{'data/'+k:v for k,v in report['fileHashes'].items()},
        **{'scripts/'+k:v for k,v in report['codeHashes'].items()},
        'data/games.csv':report['inputHashes']['resultSource'],'export/manifest.json':report['exportManifestHash']}
    for name,sha in expected.items():
        path=(retained/name).resolve()
        if not path.is_relative_to(retained.resolve()) or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise ValueError('Benchmark dependency differs')
    result=subprocess.run([sys.executable,'-c',CHILD],cwd=retained,check=True,capture_output=True,text=True,timeout=120)
    return json.loads(result.stdout)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('identity')
    parser.add_argument('--folder',type=Path,default=Path(__file__).resolve().parents[1]/'release-recovery/market-benchmark')
    args=parser.parse_args()
    print(json.dumps(replay(args.identity,args.folder)))
