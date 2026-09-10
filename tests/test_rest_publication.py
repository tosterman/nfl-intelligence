import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import deploy_release
from test_publication_preflight import fixture


class RestPublicationTests(unittest.TestCase):
    def test_invalid_edition_never_requests_deployment(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'data').mkdir()
            site, ledger = fixture()
            site['games'][0]['venue'] = 'Changed'
            for name, value in [('site', site), ('ledger', ledger)]:
                (root / f'data/{name}.json').write_text(json.dumps(value))
            with patch.object(deploy_release, 'ROOT', root), patch.dict('os.environ', {'VERCEL_PROJECT_ID': 'test'}), \
                    patch.object(deploy_release, 'release_files', return_value=[]), \
                    patch.object(deploy_release, 'request', side_effect=AssertionError('Deployment attempted')) as request:
                with self.assertRaises(ValueError):
                    deploy_release.main()
            request.assert_not_called()

    def test_receipt_write_failure_preserves_prior_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'data').mkdir()
            site, ledger = fixture()
            for name, value in [('site', site), ('ledger', ledger), ('publications', [{'prior': True}])]:
                (root / f'data/{name}.json').write_text(json.dumps(value))
            path = root / 'data/publications.json'
            before = path.read_bytes()
            meta = {'id': 'dpl_test', 'url': 'test.vercel.app', 'readyState': 'READY'}
            with patch.object(deploy_release, 'ROOT', root), patch.dict('os.environ', {'VERCEL_PROJECT_ID': 'test'}), \
                    patch.object(deploy_release, 'release_files', return_value=[]), \
                    patch.object(deploy_release, 'request', return_value=meta), \
                    patch.object(deploy_release, 'make_receipt', return_value={'snapshotHashes': ['hash']}), \
                    patch('deploy_release.urllib.request.urlopen', return_value=io.BytesIO(b'{}')), \
                    patch('publication.os.replace', side_effect=OSError('disk failure')):
                with self.assertRaises(OSError):
                    deploy_release.main()
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
