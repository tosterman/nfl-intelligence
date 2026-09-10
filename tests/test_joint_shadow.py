import sys,unittest,json,hashlib,copy,gzip
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from capture_joint_shadow import eligible_games,verify_frozen
from verify_joint_shadow import verify_capture
class JointShadowTests(unittest.TestCase):
    def test_publication_requires_exact_bytes_and_pre_kickoff_retrieval(self):
        data={'generatedAt':'2026-09-10T12:00:00+00:00','records':[{'gameId':'g','kickoff':'2026-09-11T00:00:00+00:00'}]}
        raw=json.dumps(data).encode();compressed=gzip.compress(raw)
        manifest={'compressedBytes':len(compressed),'compressedHash':hashlib.sha256(compressed).hexdigest(),'sha256':hashlib.sha256(raw).hexdigest(),'generatedAt':data['generatedAt'],'games':1}
        now=datetime(2026,9,10,16,tzinfo=timezone.utc)
        self.assertEqual(verify_capture(manifest,compressed,now,now),data)
        with self.assertRaises(ValueError):verify_capture(manifest,compressed+b'x',now,now)
        with self.assertRaises(ValueError):verify_capture(manifest,compressed,datetime(2026,9,11,tzinfo=timezone.utc),now)
    def test_changed_prior_or_solver_cannot_reuse_frozen_protocol(self):
        ref={'priorHashes':{'candidate':'a','reference':'b'},'codeHashes':{'solver':'s'},'fit':{'tieProbability':.01}}
        verify_frozen(ref,{'candidate':'a','reference':'b'},{'solver':'s','capture':'new'},ref['fit'])
        with self.assertRaises(ValueError):verify_frozen(ref,ref['priorHashes'],ref['codeHashes'],{'tieProbability':.02})
        for priors,code in [({'candidate':'changed','reference':'b'},{'solver':'s'}),({'candidate':'a','reference':'b'},{'solver':'changed'})]:
            with self.assertRaises(ValueError):verify_frozen(ref,priors,code,ref['fit'])
    def setUp(self):
        s={'gameId':'g','generatedAt':'2026-09-10T12:00:00+00:00','prediction':{'homeScore':20,'awayScore':21}}
        s['hash']=hashlib.sha256(json.dumps(s,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.local={'modelVersion':'v','generatedAt':'2026-09-10T12:00:00+00:00','games':[{'id':'g','home':'A','away':'B','kickoff':'2026-09-11T00:00:00+00:00','status':'scheduled','snapshot':s}]}
        self.now=datetime(2026,9,10,16,tzinfo=timezone.utc)
    def test_only_future_verified_identical_forecasts(self):
        self.assertEqual(len(eligible_games(self.local,copy.deepcopy(self.local),self.now)),1)
        self.assertEqual(eligible_games(self.local,self.local,datetime(2026,9,11,tzinfo=timezone.utc)),[])
        self.local['games'][0]['status']='final'
        self.assertEqual(eligible_games(self.local,self.local,self.now),[])
    def test_changed_identity_hash_and_duplicate_public_games_fail(self):
        for field in ['home','kickoff','snapshot']:
            public=copy.deepcopy(self.local);public['games'][0][field]=None
            with self.assertRaises(ValueError):eligible_games(self.local,public,self.now)
        public=copy.deepcopy(self.local);public['games']*=2
        with self.assertRaises(ValueError):eligible_games(self.local,public,self.now)
        self.local['games'][0]['snapshot']['prediction']['homeScore']=99
        with self.assertRaises(ValueError):eligible_games(self.local,self.local,self.now)
if __name__=='__main__':unittest.main()
