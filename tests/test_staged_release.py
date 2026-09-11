import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from staged_release import verify_staged_release
from deploy_release import release_paths


class StagedReleaseTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.git('init', '-q')
        self.git('config', 'core.autocrlf', 'false')
        (self.root / '.gitattributes').write_text('*.json text eol=lf\n')
        self.file = self.root / 'history.json'
        self.file.write_bytes(b'{"value": 1}\n')
        self.git('add', '.gitattributes', 'history.json')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True)

    def test_staged_contents_and_line_endings_match(self):
        self.assertEqual(verify_staged_release(self.root, [self.file]), 1)
        self.file.write_bytes(b'{"value": 1}\r\n')
        self.assertEqual(verify_staged_release(self.root, [self.file]), 1)

    def test_unstaged_changed_artifact_rejected_even_if_assumed_unchanged(self):
        self.git('update-index', '--assume-unchanged', 'history.json')
        self.file.write_bytes(b'{"value": 2}\n')
        with self.assertRaisesRegex(ValueError, 'differs from Git staging'):
            verify_staged_release(self.root, [self.file])

    def test_new_generated_file_requires_staging(self):
        added = self.root / 'new-history.json'
        added.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'absent from Git staging'):
            verify_staged_release(self.root, [self.file, added])
        self.git('add', 'new-history.json')
        self.assertEqual(verify_staged_release(self.root, [self.file, added]), 2)

    def test_deleted_and_outside_paths_rejected(self):
        self.file.unlink()
        with self.assertRaises(ValueError): verify_staged_release(self.root, [self.file])
        with self.assertRaises(ValueError): verify_staged_release(self.root, [Path(__file__)])
        with self.assertRaises(ValueError): verify_staged_release(self.root, [])

    def test_default_enumeration_rejects_unstaged_source_and_config_deletions(self):
        source = self.root / 'src/obsolete.ts'
        source.parent.mkdir()
        source.write_text('export const old = true;')
        config = self.root / 'next.config.ts'
        config.write_text('export default {};')
        for path in release_paths(self.root):
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{}')
        self.git('add', '.')
        self.assertGreater(verify_staged_release(self.root), 1)
        for path in (source, config):
            original = path.read_bytes()
            path.unlink()
            with self.assertRaisesRegex(ValueError, 'absent from the working release'):
                verify_staged_release(self.root)
            path.write_bytes(original)
