import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class RetentionModeTests(unittest.TestCase):
    def test_wrong_mode_rejects_before_mutating_either_receipt(self):
        loader=Path(subprocess.check_output(['node','-p',"require.resolve('tsx')"],cwd=ROOT,text=True).strip()).as_uri()
        for kind,flags in [('market-benchmark',[]),('checkpoint-audit',['--benchmark'])]:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temporary:
                root=Path(temporary);recovery=root/'release-recovery';recovery.mkdir()
                paths=[recovery/'market-audit-retention.json',recovery/'market-benchmark-retention.json']
                for path in paths:path.write_bytes(b'previous verified receipt')
                report=b'{}';identity=hashlib.sha256(report).hexdigest()
                envelope={'schemaVersion':1,'kind':kind,'reportHash':identity,'files':{'report.json':{'base64':base64.b64encode(report).decode()}}}
                bundle=root/'fixture.gz';bundle.write_bytes(gzip.compress(json.dumps(envelope).encode()))
                env=os.environ.copy();env['BLOB_READ_WRITE_TOKEN']=''
                result=subprocess.run(['node','--import',loader,str(ROOT/'scripts/retain_market_report.ts'),str(bundle),*flags],cwd=root,env=env,capture_output=True,text=True,timeout=30)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('Market report retention failed',result.stderr)
                for path in paths:self.assertEqual(path.read_bytes(),b'previous verified receipt')


if __name__=='__main__':unittest.main()
