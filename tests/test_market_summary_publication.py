import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from market_benchmark import digest
from publish_market_summary import publish_summary


class MarketSummaryPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for path in ('data','reviews','release-recovery/market-benchmark'):(self.root/path).mkdir(parents=True)
        self.old={'checkedAt':'2026-09-11T12:00:00Z','coverageThrough':'2026-09-11T11:00:00Z'}
        self.target=self.root/'data/market-benchmark.json';self.target.write_text(json.dumps(self.old))
        self.before=self.target.read_bytes()
        self.report={'schemaVersion':1,'checkedAt':'2026-09-11T13:00:00Z','coverageThrough':'2026-09-11T12:00:00Z','scopeGames':0,'closingCheckpointCounts':{},'pairedGameCount':0,'books':[],'records':[],'interpretation':'fixture','publicationStatus':'fixture'}
        self.report.update(resultSourceRetrievedAt='2026-09-11T11:00:00Z',editionGeneratedAt='2026-09-11T11:01:00Z')
    def prepare(self):
        identity=digest(self.report)
        (self.root/'release-recovery/market-benchmark'/f'{identity}.json').write_text(json.dumps(self.report))
        return identity
    def test_replay_failure_preserves_exact_previous_report(self):
        identity=self.prepare()
        with patch('publish_market_summary.replay',side_effect=ValueError('Mismatch')):
            with self.assertRaises(ValueError):publish_summary(self.root,identity)
        self.assertEqual(self.target.read_bytes(),self.before)
    def test_false_or_mismatched_replay_cannot_publish(self):
        identity=self.prepare()
        for proof in ({'matched':False},{'matched':True,'networkBlocked':True,'reportHash':'wrong'}):
            with patch('publish_market_summary.replay',return_value=proof):
                with self.assertRaises(ValueError):publish_summary(self.root,identity)
            self.assertEqual(self.target.read_bytes(),self.before)
    def test_verified_summary_replaces_reader_file(self):
        identity=self.prepare()
        with patch('publish_market_summary.replay',return_value={'matched':True,'networkBlocked':True,'reportHash':identity}):
            result=publish_summary(self.root,identity)
        self.assertEqual(json.loads(self.target.read_bytes()),result)
        self.assertEqual(result['reportHash'],identity)
        self.assertEqual(list((self.root/'data').glob('*.tmp')),[])
    def test_another_writer_lock_is_preserved(self):
        identity=self.prepare()
        lock=self.root/'release-recovery/market-benchmark-publish.lock';lock.write_text('other owner')
        with self.assertRaises(FileExistsError):publish_summary(self.root,identity)
        self.assertEqual(lock.read_text(),'other owner')
        self.assertEqual(self.target.read_bytes(),self.before)
    def test_older_coverage_cannot_replace_newer_report(self):
        self.report['coverageThrough']='2026-09-11T10:00:00Z';identity=self.prepare()
        with patch('publish_market_summary.replay',return_value={'matched':True,'networkBlocked':True,'reportHash':identity}):
            with self.assertRaisesRegex(ValueError,'backward'):publish_summary(self.root,identity)
        self.assertEqual(self.target.read_bytes(),self.before)
    def test_older_result_source_cannot_replace_newer_source(self):
        self.old['resultSourceRetrievedAt']='2026-09-11T12:00:00Z'
        self.target.write_text(json.dumps(self.old));before=self.target.read_bytes();identity=self.prepare()
        with patch('publish_market_summary.replay',return_value={'matched':True,'networkBlocked':True,'reportHash':identity}):
            with self.assertRaisesRegex(ValueError,'source would move backward'):publish_summary(self.root,identity)
        self.assertEqual(self.target.read_bytes(),before)
    def test_atomic_replace_failure_preserves_old_bytes_and_cleans_temporary(self):
        identity=self.prepare()
        import os
        replace=os.replace
        def fail_target(source,target):
            if target==self.target:raise OSError('Simulated replace failure')
            return replace(source,target)
        with patch('publish_market_summary.replay',return_value={'matched':True,'networkBlocked':True,'reportHash':identity}),patch('publish_market_summary.os.replace',side_effect=fail_target):
            with self.assertRaises(OSError):publish_summary(self.root,identity)
        self.assertEqual(self.target.read_bytes(),self.before)
        self.assertEqual(list((self.root/'data').glob('*.tmp')),[])


if __name__=='__main__':unittest.main()
