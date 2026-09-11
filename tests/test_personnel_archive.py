import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from personnel_archive import verify_inventory


class PersonnelArchiveTests(unittest.TestCase):
    def test_changed_or_missing_input_rejects_replay_proof(self):
        import hashlib
        proof={'data/example.json':{'sha256':hashlib.sha256(b'{}').hexdigest(),'bytes':2}}
        verify_inventory({'data/example.json':b'{}'},proof)
        for files in ({},{'data/example.json':b'[]'},{'data/example.json':b'{}','data/new.json':b'{}'}):
            with self.assertRaises(ValueError): verify_inventory(files,proof)

    def test_archive_paths_cannot_escape_the_restored_workspace(self):
        import hashlib
        for name in ('data/../secret.json','C:/secret.json','scripts/.env','data//file.json'):
            with self.assertRaises(ValueError):
                verify_inventory({name:b'{}'},{name:{'sha256':hashlib.sha256(b'{}').hexdigest(),'bytes':2}})
