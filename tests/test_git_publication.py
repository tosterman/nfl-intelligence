import copy,hashlib,io,json,sys,unittest,tempfile
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from git_publication import verified_status,make_git_receipt,capture,PUBLIC_URL
import git_publication
NOW=datetime(2026,9,10,17,tzinfo=timezone.utc)
def status():return {'id':4,'context':'Vercel','state':'success','creator':{'id':35613825,'login':'vercel[bot]'},'target_url':'https://vercel.com/khnum/nfl-intelligence/abc123','created_at':'2026-09-10T16:45:08Z'}
class GitPublicationTests(unittest.TestCase):
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
    for name,value in [('site',{}),('ledger',[]),('publications',[{'existing':'receipt'}])]:
     (root/f'data/{name}.json').write_text(json.dumps(value))
    path=root/'data/publications.json';before=path.read_bytes()
    with patch.object(git_publication,'ROOT',root),patch('git_publication.subprocess.check_output',side_effect=['main','a'*40]),patch('git_publication.subprocess.run',return_value=SimpleNamespace(returncode=0)),patch('git_publication.capture',side_effect=failure):
     with self.assertRaises(type(failure)):git_publication.main()
    self.assertEqual(path.read_bytes(),before)
    self.assertEqual(json.loads((root/'release-recovery/git-publication.json').read_text())['sourceCommit'],'a'*40)
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
