import base64
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from market_benchmark_bundle import decode,restore


class BenchmarkBundleTests(unittest.TestCase):
    def envelope(self):
        report=b'{"fixture":true}'
        return {'schemaVersion':1,'kind':'market-benchmark','reportHash':hashlib.sha256(report).hexdigest(),
            'files':{'report.json':{'sha256':hashlib.sha256(report).hexdigest(),'base64':base64.b64encode(report).decode()}}}
    def body(self,value):return gzip.compress(json.dumps(value).encode())
    def test_restore_preserves_exact_bytes_and_does_not_overwrite(self):
        envelope=self.envelope()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'restored';identity=restore(self.body(envelope),path)
            self.assertEqual((path/(identity+'.json')).read_bytes(),b'{"fixture":true}')
            with self.assertRaisesRegex(ValueError,'must not exist'):restore(self.body(envelope),path)
    def test_traversal_rejected_before_destination_creation(self):
        for name in ('../outside','scripts/../../outside','C:/outside','scripts\\outside.py'):
            envelope=self.envelope();envelope['files'][name]=envelope['files']['report.json']
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'restored'
                with self.assertRaisesRegex(ValueError,'Unsafe'):restore(self.body(envelope),path)
                self.assertFalse(path.exists())
    def test_file_hash_and_report_identity_rejected(self):
        envelope=self.envelope();envelope['files']['report.json']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'file hash'):decode(self.body(envelope))
        envelope=self.envelope();envelope['reportHash']='0'*64
        with self.assertRaisesRegex(ValueError,'report hash'):decode(self.body(envelope))
    def test_expansion_limit_applies_before_json_parsing(self):
        with patch('market_benchmark_bundle.MAX_EXPANDED',100):
            with self.assertRaisesRegex(ValueError,'Expanded'):decode(gzip.compress(b' '*101))
    def test_wrong_kind_cannot_restore_as_benchmark(self):
        envelope=self.envelope();envelope['kind']='other'
        with self.assertRaisesRegex(ValueError,'Invalid'):decode(self.body(envelope))


if __name__=='__main__':unittest.main()
