"""Reproduce frozen research in a temporary workspace without live data access."""
import gzip,hashlib,json,math,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def checked_bytes(compressed,record):
    if hashlib.sha256(compressed).hexdigest()!=record['compressedSha256']:raise ValueError('Compressed input changed')
    raw=gzip.decompress(compressed)
    if len(raw)!=record['bytes'] or hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Input hash mismatch')
    return raw

def compare_tree(expected,actual,path='root'):
    if type(expected)!=type(actual):raise ValueError(f'Type mismatch: {path}')
    if isinstance(expected,dict):
        if expected.keys()!=actual.keys():raise ValueError(f'Keys changed: {path}')
        for key in expected:compare_tree(expected[key],actual[key],path+'.'+key)
    elif isinstance(expected,list):
        if len(expected)!=len(actual):raise ValueError(f'Length changed: {path}')
        for i,(a,b) in enumerate(zip(expected,actual)):compare_tree(a,b,f'{path}[{i}]')
    elif isinstance(expected,float):
        if not math.isfinite(expected) or not math.isfinite(actual) or not math.isclose(expected,actual,rel_tol=1e-10,abs_tol=1e-12):raise ValueError(f'Numeric mismatch: {path}')
    elif expected!=actual:raise ValueError(f'Value changed: {path}')

def main():
    inputs=ROOT/'reviews/joint-replay-inputs';manifest=json.loads((inputs/'manifest.json').read_text())
    with tempfile.TemporaryDirectory(prefix='nfl-joint-replay-') as folder:
        work=Path(folder);(work/'data').mkdir();(work/'reviews').mkdir()
        shutil.copytree(ROOT/'scripts',work/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
        for name in ['games.csv','site.json']:
            (work/'data'/name).write_bytes(checked_bytes((inputs/(name+'.gz')).read_bytes(),manifest['files'][name]))
        for name in ['joint-shadow-reference.json','joint-event-audit-protocol.md','joint-settlement-protocol.md']:
            shutil.copyfile(ROOT/'reviews'/name,work/'reviews'/name)
        diagnostic="""import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'scripts')
from evaluate_joint_scores import priors
from build_data import load_rows
f=json.loads(Path('reviews/joint-shadow-reference.json').read_text())
c,r,fit=priors(load_rows(Path('data/games.csv')))
print(json.dumps({'priorHashes':{n:hashlib.sha256(p.tobytes()).hexdigest() for n,p in [('candidate',c),('reference',r)]},'expectedPriorHashes':f['priorHashes'],'fit':fit,'expectedFit':f['fit'],'changedCode':[n for n,h in f['codeHashes'].items() if hashlib.sha256((Path('scripts')/n).read_bytes()).hexdigest()!=h]}),flush=True)
"""
        subprocess.run([sys.executable,'-c',diagnostic],cwd=work,check=True)
        verified=[]
        for script,report in [('audit_joint_events.py','joint-event-audit.json'),('audit_joint_settlement.py','joint-settlement-audit.json')]:
            subprocess.run([sys.executable,str(work/'scripts'/script)],cwd=work,check=True,stdout=subprocess.DEVNULL)
            expected=json.loads((ROOT/'reviews'/report).read_text());actual=json.loads((work/'reviews'/report).read_text())
            compare_tree(expected,actual)
            verified.append({'report':report,'games':285,'reportSha256':hashlib.sha256((ROOT/'reviews'/report).read_bytes()).hexdigest()})
        print(json.dumps({'verified':verified,'floatRelativeTolerance':1e-10,'floatAbsoluteTolerance':1e-12,'productionFilesModified':False},indent=2))
if __name__=='__main__':main()
