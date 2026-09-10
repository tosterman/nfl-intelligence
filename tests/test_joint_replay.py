import sys,unittest,gzip,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from replay_joint_audits import checked_bytes,compare_tree

class JointReplayTests(unittest.TestCase):
    def test_reject_changed_source(self):
        raw=b'fixed input';compressed=gzip.compress(raw,mtime=0)
        record={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'compressedSha256':hashlib.sha256(compressed).hexdigest()}
        self.assertEqual(checked_bytes(compressed,record),raw)
        with self.assertRaises(ValueError):checked_bytes(compressed+b'x',record)
        with self.assertRaises(ValueError):checked_bytes(compressed,record|{'sha256':'0'*64})

    def test_complete_structure_and_numeric_equality(self):
        expected={'p':[.3,.7],'count':2,'id':'game'}
        compare_tree(expected,expected|{'p':[.3+1e-14,.7-1e-14]})
        for changed in [expected|{'p':[.31,.69]},expected|{'count':3},expected|{'extra':None},expected|{'p':[.3]},expected|{'id':'other'},expected|{'p':[float('nan'),.7]}]:
            with self.assertRaises(ValueError):compare_tree(expected,changed)
if __name__=='__main__':unittest.main()
