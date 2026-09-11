from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_market_benchmark import run


class BenchmarkRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.recovery=self.root/'release-recovery';self.recovery.mkdir()
        (self.recovery/'market-benchmark').mkdir();(self.root/'data').mkdir()
        self.target=self.root/'data/market-benchmark.json';self.target.write_bytes(b'previous valid summary')
        self.identity='a'*64;self.body=b'fixture package';self.sha=hashlib.sha256(self.body).hexdigest()
        self.fail=None;self.wrong=False;self.called=[]
    def command(self,args,root):
        name=next(arg for arg in args if arg.endswith(('.ts','.py')));self.called.append(name)
        if self.fail and self.fail in name:raise subprocess.CalledProcessError(1,args)
        if 'export_odds' in name:return SimpleNamespace(stdout=json.dumps({'folder':'release-recovery/export-fixture'}))
        if 'report_market_benchmark' in name:
            self.assertIn('--prepare-only',args)
            return SimpleNamespace(stdout=json.dumps({'reportHash':self.identity}))
        self.assertIn('--benchmark',args)
        receipt={'status':'verified-private-retention','reportHash':'b'*64 if self.wrong else self.identity,'sha256':self.sha,'bytes':len(self.body),'pathname':f'market-benchmarks/{self.sha}.json.gz','checkedAt':datetime.now(timezone.utc).isoformat()}
        (self.recovery/'market-benchmark-retention.json').write_text(json.dumps(receipt))
        return SimpleNamespace(stdout='')
    def test_export_grade_and_retention_failures_never_replace_reader(self):
        for failure in ('export_odds','report_market_benchmark','retain_market_report'):
            self.fail=failure
            with patch('run_market_benchmark.command',side_effect=self.command),patch('run_market_benchmark.package',return_value=self.body),patch('run_market_benchmark.publish_summary') as publish:
                with self.assertRaises(subprocess.CalledProcessError):run(self.root)
                publish.assert_not_called()
            self.assertEqual(self.target.read_bytes(),b'previous valid summary')
            self.assertFalse((self.recovery/'market-benchmark-worker.lock').exists())
            self.assertFalse(json.loads((self.recovery/'market-benchmark-run.json').read_text())['success'])
    def test_replay_failure_and_wrong_retention_identity_stop_replacement(self):
        with patch('run_market_benchmark.command',side_effect=self.command),patch('run_market_benchmark.package',side_effect=ValueError('Replay mismatch')),patch('run_market_benchmark.publish_summary') as publish:
            with self.assertRaises(ValueError):run(self.root)
            publish.assert_not_called()
        self.wrong=True
        with patch('run_market_benchmark.command',side_effect=self.command),patch('run_market_benchmark.package',return_value=self.body),patch('run_market_benchmark.publish_summary') as publish:
            with self.assertRaisesRegex(ValueError,'receipt differs'):run(self.root)
            publish.assert_not_called()
    def test_success_records_exact_retained_identity_before_replacement(self):
        with patch('run_market_benchmark.command',side_effect=self.command),patch('run_market_benchmark.package',return_value=self.body),patch('run_market_benchmark.publish_summary',return_value={'reportHash':self.identity}) as publish:
            result=run(self.root)
            publish.assert_called_once_with(self.root,self.identity)
        self.assertTrue(result['success']);self.assertEqual(result['bundleSha256'],self.sha)
        self.assertEqual(result['stage'],'complete')
    def test_other_worker_lock_is_not_removed(self):
        lock=self.recovery/'market-benchmark-worker.lock';lock.write_text('other worker')
        with self.assertRaises(FileExistsError):run(self.root)
        self.assertEqual(lock.read_text(),'other worker')


if __name__=='__main__':unittest.main()
