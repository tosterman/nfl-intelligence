import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from deploy_release import release_files, ROOT
class ReleaseFilesTests(unittest.TestCase):
    def test_runtime_json_imports_are_packaged_without_private_archives(self):
        files=release_files()
        names={entry['file'] for entry in files}
        imports=set()
        for path in (ROOT/'src').rglob('*'):
            if path.suffix in ('.ts','.tsx'):
                imports.update(re.findall(r'''["'](?:\.\./)+data/([^"']+\.json)["']''',path.read_text(encoding='utf-8')))
        self.assertTrue(imports)
        self.assertTrue({'data/'+name for name in imports}.issubset(names))
        self.assertFalse(any('.env' in name or 'sources/' in name or 'release-recovery/' in name for name in names))
        self.assertNotIn('data/ledger.json',names)
