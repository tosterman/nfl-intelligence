import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import record_publication as recorder

class ReleaseBindingTests(unittest.TestCase):
    def setUp(self):
        self.snap={'gameId':'g','generatedAt':'2026-09-10T10:00:00+00:00','prediction':{'homeWinProbability':.6}}
        self.snap['hash']=hashlib.sha256(json.dumps(self.snap,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.site={'generatedAt':'2026-09-10T10:01:00+00:00','modelVersion':'v1','games':[{'id':'g','snapshot':self.snap,'history':[self.snap]},{'id':'future','snapshot':None,'history':[]}]}
        self.artifact={**self.site,'games':[self.site['games'][0]]}
        self.deployment={'readyState':'READY','id':'dpl_fixture','url':'fixture.vercel.app'}
    def test_exact_intended_artifact_records_digest(self):
        receipt=recorder.make_receipt(self.deployment,self.artifact,[self.snap],expected_site=self.site)
        expected=hashlib.sha256(json.dumps(self.artifact,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.assertEqual(receipt['artifactSha256'],expected)
    def test_stale_generation_rejected_even_with_valid_snapshots(self):
        artifact=copy.deepcopy(self.artifact);artifact['generatedAt']='2026-09-09T10:01:00+00:00'
        with self.assertRaisesRegex(ValueError,'intended'):
            recorder.make_receipt(self.deployment,artifact,[self.snap],expected_site=self.site)
    def test_partial_game_set_rejected(self):
        site=copy.deepcopy(self.site);site['games'].append({**site['games'][0],'id':'other'})
        with self.assertRaisesRegex(ValueError,'intended'):
            recorder.make_receipt(self.deployment,self.artifact,[self.snap],expected_site=site)
    def test_game_display_tampering_rejected(self):
        artifact=copy.deepcopy(self.artifact);artifact['games'][0]['status']='final'
        with self.assertRaisesRegex(ValueError,'intended'):
            recorder.make_receipt(self.deployment,artifact,[self.snap],expected_site=self.site)
    def test_known_hash_label_is_not_enough(self):
        artifact=copy.deepcopy(self.artifact);artifact['games'][0]['history'][0]['prediction']['homeWinProbability']=.99
        site={**self.site,'games':artifact['games']}
        with self.assertRaisesRegex(ValueError,'canonical'):
            recorder.make_receipt(self.deployment,artifact,[self.snap],expected_site=site)
    def test_javascript_integral_float_serialization_preserves_authenticity(self):
        self.snap['prediction']['homeMargin']=0.0
        self.snap['hash']=hashlib.sha256(json.dumps({k:v for k,v in self.snap.items() if k!='hash'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
        artifact=json.loads(recorder.wire_json(self.artifact))
        self.assertIsInstance(artifact['games'][0]['history'][0]['prediction']['homeMargin'],int)
        receipt=recorder.make_receipt(self.deployment,artifact,[self.snap],expected_site=self.site)
        self.assertEqual(receipt['snapshotHashes'],[self.snap['hash']])
    def test_boolean_is_not_interchangeable_with_numeric_zero(self):
        self.site['games'][0]['neutral']=0
        artifact=copy.deepcopy(self.artifact);artifact['games'][0]['neutral']=False
        with self.assertRaisesRegex(ValueError,'intended'):
            recorder.make_receipt(self.deployment,artifact,[self.snap],expected_site=self.site)

class ArchiveRecoveryTests(unittest.TestCase):
    def test_concurrent_advance_rebases_then_retries_without_force(self):
        import push_publication
        from types import SimpleNamespace
        calls=[]
        def run(args,check):
            calls.append(args)
            return SimpleNamespace(returncode=1 if len(calls)==1 else 0)
        push_publication.push_archive('main',run=run)
        self.assertEqual(calls,[['git','push','origin','HEAD:refs/heads/main'],['git','fetch','origin','refs/heads/main'],['git','rebase','FETCH_HEAD'],['git','push','origin','HEAD:refs/heads/main']])
    def test_conflicting_remote_history_aborts_without_second_push(self):
        import push_publication
        from types import SimpleNamespace
        calls=[]
        def run(args,check):
            calls.append(args)
            return SimpleNamespace(returncode=1 if args[1] in ['push','rebase'] and '--abort' not in args else 0)
        with self.assertRaisesRegex(RuntimeError,'conflicts'):
            push_publication.push_archive('main',run=run)
        self.assertEqual(calls[-1],['git','rebase','--abort'])
        self.assertEqual(sum(c[1]=='push' for c in calls),1)
    def test_deployment_recovery_metadata_excludes_secrets(self):
        import deploy_release
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(deploy_release,'ROOT',Path(folder)):
                deploy_release.save_recovery_metadata({'id':'dpl_fixture','url':'fixture.vercel.app','readyState':'READY','token':'secret','env':{'PASSWORD':'secret'}})
            saved=json.loads((Path(folder)/'release-recovery/deployment.json').read_text())
        self.assertEqual(saved,{'id':'dpl_fixture','url':'fixture.vercel.app','readyState':'READY'})

if __name__=='__main__':unittest.main()
