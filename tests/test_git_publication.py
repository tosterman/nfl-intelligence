import copy,hashlib,io,json,sys,unittest,tempfile
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from git_publication import verified_status,make_git_receipt,capture,PUBLIC_URL
import git_publication
from test_publication_preflight import fixture
NOW=datetime(2026,9,10,17,tzinfo=timezone.utc)
def status():return {'id':4,'context':'Vercel','state':'success','creator':{'id':35613825,'login':'vercel[bot]'},'target_url':'https://vercel.com/khnum/nfl-intelligence/abc123','created_at':'2026-09-10T16:45:08Z'}
class GitPublicationTests(unittest.TestCase):
 def setUp(self):
  # These fixtures isolate publication orchestration. Actual Git content checks
  # run in temporary repositories in test_staged_release.py.
  guard=patch('git_publication.verify_staged_release',return_value=1)
  self.guard=guard.start();self.addCleanup(guard.stop)
 def test_staged_release_failure_stops_before_commit_push_and_capture(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'data').mkdir();site,ledger=fixture()
   for name,value in [('site',site),('ledger',ledger)]:
    (root/f'data/{name}.json').write_text(json.dumps(value))
   self.guard.side_effect=ValueError('Release file differs from Git staging')
   with patch.object(git_publication,'ROOT',root),patch('git_publication.subprocess.check_output',return_value='main'),patch('git_publication.subprocess.run',return_value=SimpleNamespace(returncode=0)) as command,patch('git_publication.capture') as capture:
    with self.assertRaisesRegex(ValueError,'differs from Git staging'):git_publication.main()
   self.assertFalse(any(call.args[0][:2] in (['git','commit'],['git','push']) for call in command.call_args_list))
   capture.assert_not_called()
 def test_generated_benchmark_and_personnel_audits_are_staged_before_release_validation(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'data').mkdir();site,ledger=fixture()
   for name,value in [('site',site),('ledger',ledger)]:
    (root/f'data/{name}.json').write_text(json.dumps(value))
   def validate_staging(_):
    additions=[call.args[0][2:] for call in command.call_args_list if call.args[0][:2]==['git','add']]
    for required in ('data/market-benchmark.json','reviews/personnel-identity-audit.json','reviews/player-usage-audit.json'):
     self.assertIn(required,[path for paths in additions for path in paths])
    raise ValueError('Stop after staging validation')
   self.guard.side_effect=validate_staging
   with patch.object(git_publication,'ROOT',root),patch('git_publication.subprocess.check_output',return_value='main'),patch('git_publication.subprocess.run',return_value=SimpleNamespace(returncode=0)) as command,patch('git_publication.capture') as capture:
    with self.assertRaisesRegex(ValueError,'Stop after staging validation'):git_publication.main()
   self.assertFalse(any(call.args[0][:2] in (['git','commit'],['git','push']) for call in command.call_args_list))
   capture.assert_not_called()
 def test_cooldown_requires_trusted_latest_limit_and_expires_without_claiming_capacity(self):
  limited={**status(),'state':'failure','target_url':'https://vercel.com/khnum?upgradeToPro=build-rate-limit'}
  deadline=git_publication.provider_cooldown([limited],NOW)
  self.assertEqual(deadline.isoformat(),'2026-09-11T16:45:08+00:00')
  self.assertIsNone(git_publication.provider_cooldown([limited],deadline))
  self.assertIsNone(git_publication.provider_cooldown([limited,{**status(),'id':5}],NOW))
  for state in ['success','pending','failure']:
   with self.assertRaisesRegex(ValueError,'Untrusted'):
    git_publication.provider_cooldown([limited,{**status(),'id':5,'state':state,'creator':{'id':1,'login':'spoof'}}],NOW)
  with self.assertRaisesRegex(ValueError,'Untrusted'):
   git_publication.provider_cooldown([{**limited,'creator':{'id':1,'login':'vercel[bot]'}}],NOW)
  with self.assertRaisesRegex(ValueError,'time'):
   git_publication.provider_cooldown([{**limited,'created_at':'2027-01-01T00:00:00Z'}],NOW)
 def test_active_cooldown_preserves_intent_without_push_or_capture(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'data').mkdir();site,ledger=fixture()
   for name,value in [('site',site),('ledger',ledger)]:
    (root/f'data/{name}.json').write_text(json.dumps(value))
   with patch.object(git_publication,'ROOT',root),patch('git_publication.subprocess.check_output',side_effect=['main','a'*40]),patch('git_publication.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='[]')) as command,patch('git_publication.check_provider_cooldown',side_effect=ValueError('cooldown active')),patch('git_publication.capture') as capture:
    with self.assertRaisesRegex(ValueError,'cooldown active'):git_publication.main()
   self.assertFalse(any(call.args[0][1]=='push' for call in command.call_args_list))
   capture.assert_not_called()
   self.assertEqual(json.loads((root/'release-recovery/git-publication.json').read_text())['sourceCommit'],'a'*40)
 def test_rejected_push_retains_intended_commit_without_receipt_or_capture(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'data').mkdir();site,ledger=fixture()
   for name,value in [('site',site),('ledger',ledger),('publications',[{'existing':'receipt'}])]:
    (root/f'data/{name}.json').write_text(json.dumps(value))
   before=(root/'data/publications.json').read_bytes()
   def command(args,**kwargs):
    if args[1]=='push':raise git_publication.subprocess.CalledProcessError(1,args)
    return SimpleNamespace(returncode=0,stdout='[]')
   with patch.object(git_publication,'ROOT',root),patch('git_publication.subprocess.check_output',side_effect=['main','a'*40]),patch('git_publication.subprocess.run',side_effect=command),patch('git_publication.capture') as capture:
    with self.assertRaises(git_publication.subprocess.CalledProcessError):git_publication.main()
   capture.assert_not_called()
   self.assertEqual((root/'data/publications.json').read_bytes(),before)
   recovery=json.loads((root/'release-recovery/git-publication.json').read_text())
   self.assertEqual(recovery['sourceCommit'],'a'*40)
   self.assertEqual(recovery['evidenceType'],'publication-intent-only')
 def test_intent_disk_failure_stops_before_remote_push(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'data').mkdir();site,ledger=fixture()
   for name,value in [('site',site),('ledger',ledger)]:
    (root/f'data/{name}.json').write_text(json.dumps(value))
   with patch.object(git_publication,'ROOT',root),patch('git_publication.subprocess.check_output',side_effect=['main','a'*40]),patch('git_publication.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='[]')) as command,patch('git_publication.write_receipts',side_effect=OSError('Simulated disk failure')),patch('git_publication.capture') as capture:
    with self.assertRaises(OSError):git_publication.main()
   self.assertFalse(any(call.args[0][1]=='push' for call in command.call_args_list))
   capture.assert_not_called()
 def test_provider_limit_is_classified_without_accepting_non_deployment_url(self):
  limited={**status(),'state':'failure','target_url':'https://vercel.com/khnum?upgradeToPro=build-rate-limit'}
  with self.assertRaisesRegex(ValueError,'build rate limit'):verified_status([limited],NOW)
  with self.assertRaisesRegex(ValueError,'Untrusted'):verified_status([{**limited,'creator':{'id':1,'login':'vercel[bot]'}}],NOW)
  with self.assertRaisesRegex(ValueError,'Unexpected'):verified_status([{**limited,'state':'success'}],NOW)
 def test_only_trusted_latest_success_with_expected_project(self):
  self.assertEqual(verified_status([status()],NOW)['id'],4)
  pending={**status(),'id':5,'state':'pending'}
  self.assertIsNone(verified_status([status(),pending],NOW))
  for change in [{'creator':{'id':1,'login':'vercel[bot]'}},{'target_url':'https://vercel.com/other/nfl-intelligence/abc123'},{'target_url':status()['target_url']+'?redirect=elsewhere'},{'created_at':'2026-09-11T00:00:00Z'}]:
   with self.assertRaises(ValueError):verified_status([{**status(),**change}],NOW)
  with self.assertRaises(ValueError):verified_status([{**status(),'state':'failure'}],NOW)
 def test_receipt_requires_exact_public_artifact_and_valid_local_history(self):
  snap={'gameId':'g','generatedAt':'2026-09-10T10:00:00Z','prediction':{'homeWinProbability':.6}}
  snap['hash']=hashlib.sha256(json.dumps(snap,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  site={'generatedAt':'2026-09-10T10:00:00Z','modelVersion':'v1','games':[{'id':'g','snapshot':snap,'history':[snap]}]}
  receipt=make_git_receipt([status()],'a'*40,site,[snap],site,NOW)
  self.assertEqual(receipt['evidenceType'],'github-status-and-public-capture')
  self.assertEqual(receipt['providerDeploymentRef'],'abc123');self.assertNotIn('deploymentId',receipt)
  self.assertEqual(receipt['publishedAt'],NOW.isoformat());self.assertEqual(receipt['snapshotHashes'],[snap['hash']])
  bad=copy.deepcopy(site);bad['generatedAt']='2026-09-09T10:00:00Z'
  with self.assertRaises(ValueError):make_git_receipt([status()],'a'*40,bad,[snap],site,NOW)
  with self.assertRaises(ValueError):make_git_receipt([], 'a'*40,site,[snap],site,NOW)
  with self.assertRaises(ValueError):make_git_receipt([status()],'main',site,[snap],site,NOW)
 def test_alias_mismatch_retries_and_captures_only_matching_bytes(self):
  snap={'gameId':'g','generatedAt':'2026-09-10T10:00:00Z','prediction':{'homeWinProbability':.6}}
  snap['hash']=hashlib.sha256(json.dumps(snap,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  site={'generatedAt':'2026-09-10T10:00:00Z','modelVersion':'v1','games':[{'id':'g','snapshot':snap,'history':[snap]}]}
  class Response(io.BytesIO):
   def geturl(self):return PUBLIC_URL+'/api/forecasts'
  old={**site,'generatedAt':'2026-09-09T00:00:00Z'}
  responses=[Response(json.dumps(value).encode()) for value in [old,site]]
  provider={**status(),'created_at':'2020-01-01T00:00:00Z'}
  command=SimpleNamespace(returncode=0,stdout=json.dumps([provider]))
  with patch('git_publication.subprocess.run',return_value=command),patch('git_publication.urllib.request.urlopen',side_effect=responses) as fetch,patch('git_publication.time.sleep') as sleep:
   receipt=capture('a'*40,site,[snap])
  self.assertEqual(fetch.call_count,2);self.assertEqual(sleep.call_count,1)
  self.assertEqual(receipt['snapshotHashes'],[snap['hash']])
 def test_status_lookup_failure_does_not_request_public_artifact(self):
  with patch('git_publication.subprocess.run',return_value=SimpleNamespace(returncode=1)),patch('git_publication.urllib.request.urlopen') as fetch:
   with self.assertRaises(RuntimeError):capture('a'*40,{},[])
   fetch.assert_not_called()
 def test_failed_capture_preserves_receipts_and_retains_recovery_identity(self):
  for failure in [ValueError('Native deployment failed'),TimeoutError('Alias remained mismatched')]:
   with self.subTest(failure=type(failure).__name__),tempfile.TemporaryDirectory() as folder:
    root=Path(folder);(root/'data').mkdir()
    site,ledger=fixture()
    for name,value in [('site',site),('ledger',ledger),('publications',[{'existing':'receipt'}])]:
     (root/f'data/{name}.json').write_text(json.dumps(value))
    path=root/'data/publications.json';before=path.read_bytes()
    with patch.object(git_publication,'ROOT',root),patch('git_publication.subprocess.check_output',side_effect=['main','a'*40]),patch('git_publication.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='[]')),patch('git_publication.capture',side_effect=failure):
     with self.assertRaises(type(failure)):git_publication.main()
    self.assertEqual(path.read_bytes(),before)
    self.assertEqual(json.loads((root/'release-recovery/git-publication.json').read_text())['sourceCommit'],'a'*40)
 def test_invalid_edition_fails_before_git_mutation_or_capture(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'data').mkdir();site,ledger=fixture()
   site['games'][0]['venue']='Changed venue'
   for name,value in [('site',site),('ledger',ledger)]:
    (root/f'data/{name}.json').write_text(json.dumps(value))
   with patch.object(git_publication,'ROOT',root),patch('git_publication.subprocess.check_output',return_value='main'),patch('git_publication.subprocess.run') as command,patch('git_publication.capture') as capture:
    with self.assertRaises(ValueError):git_publication.main()
   command.assert_not_called();capture.assert_not_called()
 def test_atomic_receipt_write_failure_preserves_old_bytes_and_cleans_temporary_file(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'publications.json';path.write_text('[{"old":true}]');before=path.read_bytes()
   for operation in ['publication.os.replace','publication.os.fsync']:
    with patch(operation,side_effect=OSError('Simulated disk failure')):
     with self.assertRaises(OSError):git_publication.write_receipts(path,[{'old':True},{'new':True}])
    self.assertEqual(path.read_bytes(),before)
    self.assertEqual(list(Path(folder).iterdir()),[path])
   git_publication.write_receipts(path,[{'old':True},{'new':True}])
   self.assertEqual(json.loads(path.read_text()),[{'old':True},{'new':True}])
 def test_unserializable_receipt_does_not_truncate_prior_evidence(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'publications.json';path.write_text('[{"old":true}]');before=path.read_bytes()
   with self.assertRaises(ValueError):git_publication.write_receipts(path,[{'old':True},{'bad':float('nan')}])
   self.assertEqual(path.read_bytes(),before)
   self.assertEqual(list(Path(folder).iterdir()),[path])
 def test_persistent_artifact_mismatch_times_out_without_receipt(self):
  class Response(io.BytesIO):
   def geturl(self):return PUBLIC_URL+'/api/forecasts'
  command=SimpleNamespace(returncode=0,stdout=json.dumps([{**status(),'created_at':'2020-01-01T00:00:00Z'}]))
  expected={'generatedAt':'now','modelVersion':'v1','games':[]}
  with patch('git_publication.subprocess.run',return_value=command),patch('git_publication.urllib.request.urlopen',side_effect=lambda *args,**kwargs:Response(b'{}')) as fetch,patch('git_publication.time.monotonic',side_effect=[0,0,1,3]),patch('git_publication.time.sleep'):
   with self.assertRaises(TimeoutError):capture('a'*40,expected,[],timeout=2)
  self.assertEqual(fetch.call_count,2)
if __name__=='__main__':unittest.main()
