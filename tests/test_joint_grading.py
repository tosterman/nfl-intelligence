import sys,unittest,copy,tempfile,json
from unittest.mock import patch
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from grade_joint_shadow import grade,load_shadows,ROOT
import grade_joint_shadow
class JointGradingTests(unittest.TestCase):
    def setUp(self):
        p=np.zeros((101,101));p[21,17]=1
        self.record={'gameId':'g','season':2026,'week':1,'type':'REG','home':'A','away':'B','kickoff':'2026-09-11T00:00:00+00:00','candidate':p.tolist(),'reference':p.tolist()}
        self.shadow={'archiveHash':'a','generatedAt':'2026-09-10T12:00:00+00:00','publishedAt':'2026-09-10T13:00:00+00:00','record':self.record}
        self.game={k:v for k,v in self.record.items() if k not in ['gameId','candidate','reference']}|{'id':'g','status':'final','actualHome':21,'actualAway':17}
        self.now=datetime(2026,9,12,tzinfo=timezone.utc)
    def test_first_published_capture_is_used_not_best_or_latest(self):
        later=copy.deepcopy(self.shadow);later['publishedAt']='2026-09-10T14:00:00+00:00';later['record']['candidate']=np.zeros((101,101)).tolist()
        result=grade([later,self.shadow],[self.game],self.now)
        self.assertEqual(result['graded'],1);self.assertEqual(result['summary']['candidate']['jointLogScore'],0)
        self.assertIsNone(result['pairedJointLogScore']['interval95'])
    def test_missing_results_and_changed_identity_are_not_scored(self):
        result=grade([self.shadow],[self.game|{'status':'scheduled'}],self.now)
        self.assertEqual(result['pending'],1);self.assertIsNone(result['summary'])
        result=grade([self.shadow],[self.game|{'kickoff':'2026-09-11T01:00:00+00:00'}],self.now)
        self.assertEqual(result['excluded'],1);self.assertIsNone(result['summary'])
        equivalent=self.game|{'kickoff':'2026-09-10T20:00:00-04:00'}
        self.assertEqual(grade([self.shadow],[equivalent],self.now)['graded'],1)
    def test_late_receipt_and_invalid_final_fail(self):
        with self.assertRaises(ValueError):grade([self.shadow|{'publishedAt':self.record['kickoff']}],[self.game],self.now)
        with self.assertRaises(ValueError):grade([self.shadow],[self.game|{'actualHome':float('nan')}],self.now)
    def test_actual_archived_publication_validates(self):
        shadows=load_shadows(ROOT/'reviews/joint-shadow')
        self.assertGreaterEqual(len(shadows),15)
    def test_changed_current_scorer_cannot_regrade_frozen_protocol(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'reviews').mkdir();(root/'scripts').mkdir()
            (root/'reviews/joint-shadow-reference.json').write_text(json.dumps({'codeHashes':{'evaluate_joint_scores.py':'expected'}}))
            (root/'scripts/evaluate_joint_scores.py').write_text('changed scorer')
            with patch.object(grade_joint_shadow,'ROOT',root),self.assertRaisesRegex(ValueError,'scoring implementation'):load_shadows(root/'reviews')
if __name__=='__main__':unittest.main()
