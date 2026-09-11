import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import verify_personnel_publication as checker

class Response(io.BytesIO):
    def __init__(self,status,value):
        super().__init__(json.dumps(value).encode());self.status=status

class PersonnelReadbackTests(unittest.TestCase):
    def test_transport_failure_is_retained_and_retried(self):
        with tempfile.TemporaryDirectory(prefix='nfl-readback-') as folder:
            root=Path(folder);(root/'reviews').mkdir()
            (root/'reviews/personnel-incremental-publication.json').write_text(json.dumps({'mode':'published','publication':{'sha256':'a'*64}}))
            calls=[]
            def response(*args,**kwargs):
                calls.append(1)
                if len(calls)<=3:raise TimeoutError('network timeout')
                return Response(200,{'status':'ok','publicationHash':'a'*64})
            with patch.object(checker,'ROOT',root),patch.object(checker.time,'sleep'),patch.object(checker.urllib.request,'urlopen',side_effect=response):
                checker.main('http://localhost:3000')
            report=json.loads((root/'reviews/personnel-public-readback.json').read_bytes())
            self.assertEqual(len(report['attempts']),2)
            self.assertEqual(report['attempts'][0]['checks'][0]['errorType'],'TimeoutError')

    def test_exact_publication_with_unavailable_feed_is_reported_but_not_healthy(self):
        with tempfile.TemporaryDirectory(prefix='nfl-readback-') as folder:
            root=Path(folder);(root/'reviews').mkdir()
            (root/'reviews/personnel-incremental-publication.json').write_text(json.dumps({'mode':'published','publication':{'sha256':'a'*64}}))
            with patch.object(checker,'ROOT',root),patch.object(checker.urllib.request,'urlopen',side_effect=lambda *_args,**_kwargs:Response(503,{'status':'unavailable','publicationHash':'a'*64})):
                with self.assertRaisesRegex(ValueError,'feed is unavailable'):checker.main('http://localhost:3000')
            report=json.loads((root/'reviews/personnel-public-readback.json').read_bytes())
            self.assertEqual(len(report['checks']),3)
            self.assertTrue(all(c['httpStatus']==503 for c in report['checks']))

    def test_healthy_old_publication_does_not_pass(self):
        with tempfile.TemporaryDirectory(prefix='nfl-readback-') as folder:
            root=Path(folder);(root/'reviews').mkdir()
            (root/'reviews/personnel-incremental-publication.json').write_text(json.dumps({'mode':'published','publication':{'sha256':'a'*64}}))
            with patch.object(checker,'ROOT',root),patch.object(checker.time,'monotonic',side_effect=[0,121]),patch.object(checker.urllib.request,'urlopen',side_effect=lambda *_args,**_kwargs:Response(200,{'status':'ok','publicationHash':'b'*64})):
                with self.assertRaisesRegex(ValueError,'exact personnel publication'):checker.main('http://localhost:3000')
            self.assertTrue((root/'reviews/personnel-public-readback.json').exists())
