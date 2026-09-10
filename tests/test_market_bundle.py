import base64
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_market_audit import package_report

class MarketBundleTests(unittest.TestCase):
    def fixture(self, root):
        files={'data/site.json':b'{"games":[]}', 'scripts/market_pairing.py':b'# code\n',
               'reviews/market-pairing-protocol.md':b'protocol', 'export/manifest.json':b'{"captures":[]}'}
        for name, body in files.items():
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
        sha=lambda name:hashlib.sha256(files[name]).hexdigest()
        report={'inputHashes':{'site.json':sha('data/site.json')},'codeHashes':{'market_pairing.py':sha('scripts/market_pairing.py')},
                'exportManifestHash':sha('export/manifest.json'),'protocolHash':sha('reviews/market-pairing-protocol.md')}
        return self.report(root,report)
    def report(self,root,report):
        body=json.dumps(report).encode();digest=hashlib.sha256(body).hexdigest()
        folder=root/'release-recovery/market-pairing';folder.mkdir(parents=True,exist_ok=True)
        (folder/(digest+'.json')).write_bytes(body)
        return {'reportHash':digest}
    def test_exact_allowlisted_bytes_roundtrip_without_secrets(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);summary=self.fixture(root)
            (root/'.env.local').write_text('SECRET=private')
            body=package_report(root,root/'export',summary)
            bundle=json.loads(gzip.decompress(body))
            self.assertNotIn('.env.local',bundle['files'])
            self.assertEqual(bundle['reportHash'],summary['reportHash'])
            for entry in bundle['files'].values():
                self.assertEqual(hashlib.sha256(base64.b64decode(entry['base64'])).hexdigest(),entry['sha256'])
            self.assertEqual(body,package_report(root,root/'export',summary))
    def test_changed_dependency_or_report_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);summary=self.fixture(root)
            (root/'data/site.json').write_text('changed')
            with self.assertRaises(ValueError):package_report(root,root/'export',summary)
            summary=self.fixture(root)
            (root/'release-recovery/market-pairing'/(summary['reportHash']+'.json')).write_text('{}')
            with self.assertRaises(ValueError):package_report(root,root/'export',summary)
    def test_unknown_input_path_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.fixture(root)
            summary=self.report(root,{'inputHashes':{'../.env.local':'a'*64}})
            with self.assertRaises(ValueError):package_report(root,root/'export',summary)
