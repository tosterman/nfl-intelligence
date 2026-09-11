"""Export, grade, replay and privately retain before changing the local public audit."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from market_benchmark_bundle import package
from market_pairing import instant
from publish_market_summary import publish_summary,atomic_json

ROOT=Path(__file__).resolve().parents[1]


def command(args,root):
    return subprocess.run(args,cwd=root,check=True,capture_output=True,text=True,timeout=180)


def run(root=ROOT):
    recovery=root/'release-recovery';recovery.mkdir(exist_ok=True)
    lock=recovery/'market-benchmark-worker.lock'
    with lock.open('x') as handle:handle.write(datetime.now(timezone.utc).isoformat())
    state={'schemaVersion':1,'startedAt':datetime.now(timezone.utc).isoformat(),'success':False,'stage':'export'}
    try:
        receipt_path=recovery/'market-benchmark-retention.json';receipt_path.unlink(missing_ok=True)
        exported=command(['node','--import','tsx','scripts/export_odds_evidence.ts'],root)
        export=(root/json.loads(exported.stdout)['folder']).resolve()
        if not export.is_relative_to(recovery.resolve()):raise ValueError('Unexpected export destination')
        state['stage']='grade'
        prepared=command([sys.executable,'scripts/report_market_benchmark.py','--export',str(export),'--prepare-only'],root)
        identity=json.loads(prepared.stdout)['reportHash']
        state['reportHash']=identity
        state['stage']='replay-and-package'
        folder=recovery/'market-benchmark'
        body=package(identity,folder)
        sha=hashlib.sha256(body).hexdigest();destination=folder/(sha+'.bundle.json.gz')
        if destination.exists():
            if destination.read_bytes()!=body:raise ValueError('Existing package differs')
        else:
            with destination.open('xb') as output:output.write(body)
        state['stage']='private-retention'
        command(['node','--import','tsx','scripts/retain_market_report.ts',str(destination),'--benchmark'],root)
        receipt=json.loads(receipt_path.read_text())
        if (receipt.get('status')!='verified-private-retention' or receipt.get('reportHash')!=identity or
            receipt.get('sha256')!=sha or receipt.get('bytes')!=len(body) or
            receipt.get('pathname')!=f'market-benchmarks/{sha}.json.gz' or
            not instant(state['startedAt'])<=instant(receipt['checkedAt'])<=datetime.now(timezone.utc)):
            raise ValueError('Private retention receipt differs')
        state['stage']='local-replacement'
        summary=publish_summary(root,identity)
        if summary['reportHash']!=identity:raise ValueError('Published summary identity differs')
        state.update(stage='complete',success=True,bundleSha256=sha)
        return state
    finally:
        state['completedAt']=datetime.now(timezone.utc).isoformat()
        try:atomic_json(recovery/'market-benchmark-run.json',state)
        finally:lock.unlink()


if __name__=='__main__':
    try:print(json.dumps(run()))
    except Exception:
        print('Benchmark refresh failed; inspect the stage report. No new successful run is claimed.',file=sys.stderr)
        sys.exit(1)
