import gzip
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from replay_retained_fixture import restore


class RetainedFixtureTests(unittest.TestCase):
    def test_restore_binds_bytes_and_rejects_unsafe_paths_and_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'source'; source.mkdir()
            raw = b'fixture'; compressed = gzip.compress(raw, mtime=0)
            sha = hashlib.sha256(raw).hexdigest(); blob = sha + '.gz'
            (source / blob).write_bytes(compressed)
            entry = {'path': 'data/site.json', 'blob': blob, 'sha256': sha,
                     'compressedSha256': hashlib.sha256(compressed).hexdigest(), 'bytes': len(raw)}
            def run(entries):
                (source / 'manifest.json').write_text(json.dumps({'files': entries}))
                return restore(source, root / 'target')
            run([entry])
            self.assertEqual((root / 'target/data/site.json').read_bytes(), raw)
            for path in ['../outside', '/absolute', 'data/../outside', 'data\\site.json']:
                with self.assertRaises(ValueError): run([dict(entry, path=path)])
            with self.assertRaises(ValueError): run([entry, entry])
            with self.assertRaises(ValueError): run([dict(entry, sha256='0'*64)])
            (source / blob).write_bytes(b'changed')
            with self.assertRaises(ValueError): run([entry])
