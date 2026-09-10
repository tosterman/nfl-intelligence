import copy,hashlib,json,sys,unittest
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from git_publication import verified_status,make_git_receipt
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
  self.assertEqual(receipt['publishedAt'],NOW.isoformat());self.assertEqual(receipt['snapshotHashes'],[snap['hash']])
  bad=copy.deepcopy(site);bad['generatedAt']='2026-09-09T10:00:00Z'
  with self.assertRaises(ValueError):make_git_receipt([status()],'a'*40,bad,[snap],site,NOW)
  with self.assertRaises(ValueError):make_git_receipt([], 'a'*40,site,[snap],site,NOW)
  with self.assertRaises(ValueError):make_git_receipt([status()],'main',site,[snap],site,NOW)
if __name__=='__main__':unittest.main()
