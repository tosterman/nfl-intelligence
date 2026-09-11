import json
import hashlib
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from refresh_personnel_worker import collect,derive,replay_sources,COLLECTORS,DERIVED_FILES


class PersonnelRefreshTests(unittest.TestCase):
    def test_optimized_python_still_rejects_modified_quarterback_roles(self):
        repo=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix='nfl-personnel-replay-') as folder:
            root=Path(folder);(root/'data').mkdir();(root/'reviews').mkdir()
            shutil.copytree(repo/'scripts',root/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
            for directory in ('personnel-sources','quarterback-sources'):
                shutil.copytree(repo/'data'/directory,root/'data'/directory)
            p=json.loads((repo/'data/personnel.json').read_bytes())
            encoded=(json.dumps(p,sort_keys=True,separators=(',',':'))+'\n').encode()
            (root/'data/personnel.json').write_bytes(encoded)
            q=json.loads((repo/'data/quarterbacks.json').read_bytes())
            next(iter(q['teams'].values()))['listedFirst']='tampered'
            (root/'data/quarterbacks.json').write_text(json.dumps(q))
            with patch.dict(os.environ,{'PYTHONOPTIMIZE':'1'}):
                with self.assertRaisesRegex(ValueError,'source replay failed'):
                    replay_sources(root,hashlib.sha256(encoded).hexdigest())
            self.assertIn('Quarterback roles do not replay',(root/'reviews/source-replay.log').read_text())

    def test_interrupted_collectors_preserve_original_snapshots_and_attempt_all_feeds(self):
        with tempfile.TemporaryDirectory(prefix='nfl-personnel-test-') as folder:
            root=Path(folder);(root/'data').mkdir()
            original=b'{"season":2026,"retrievedAt":"2026-09-01T00:00:00Z"}'
            for _,pointer,_,_ in COLLECTORS:(root/'data'/pointer).write_bytes(original)
            called=[]
            def interrupted(root,script):
                called.append(script)
                pointer=next(row[1] for row in COLLECTORS if row[0]==script)
                (root/'data'/pointer).write_bytes(b'truncated')
                return 124
            results=collect(root,interrupted)
            self.assertEqual(len(called),3)
            self.assertTrue(all(row['exitCode']==124 for row in results))
            for _,pointer,state,failure in COLLECTORS:
                self.assertEqual((root/'data'/pointer).read_bytes(),original)
                self.assertEqual(json.loads((root/'data'/state).read_bytes())['status'],failure)

    def test_first_failed_derivation_stops_dependent_steps(self):
        with tempfile.TemporaryDirectory(prefix='nfl-derived-test-') as folder:
            root=Path(folder)
            for name in DERIVED_FILES:
                (root/name).parent.mkdir(parents=True,exist_ok=True)
                (root/name).write_bytes(b'original')
            calls=[]
            def failure(root,script):
                calls.append(script)
                for name in DERIVED_FILES:(root/name).write_bytes(b'')
                return 1
            kind,results=derive(root,failure)
            self.assertEqual(kind,'identity-audit')
            self.assertEqual(calls,['audit_personnel_identity.py'])
            self.assertEqual(results[0]['exitCode'],1)
            for name in DERIVED_FILES:self.assertEqual((root/name).read_bytes(),b'original')
