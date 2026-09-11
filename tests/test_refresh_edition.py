import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from refresh_edition import run


class RefreshEditionTests(unittest.TestCase):
    def test_success_normalizes_before_retention_without_changing_values_or_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir(); (root / 'data').mkdir()
            payload = b'{"text":"escaped \\r\\n preserved","prediction":42.5}\r\n'
            (root / 'scripts/refresh.py').write_text('from pathlib import Path\nPath("data/site.json").write_bytes('+repr(payload)+')\n')
            (root / 'data/ledger.json').write_bytes(b'unchanged ledger bytes\r\n')
            run(root)
            actual = (root / 'data/site.json').read_bytes()
            self.assertEqual(actual, payload.replace(b'\r\n',b'\n'))
            self.assertEqual(json.loads(actual),json.loads(payload))
            self.assertEqual((root / 'data/ledger.json').read_bytes(),b'unchanged ledger bytes\r\n')
            run(root)
            self.assertEqual((root / 'data/site.json').read_bytes(),actual)

    def test_failed_builder_does_not_normalize_previous_edition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir(); (root / 'data').mkdir()
            (root / 'scripts/refresh.py').write_text('raise SystemExit(1)\n')
            previous = b'{"previous":true}\r\n'
            (root / 'data/site.json').write_bytes(previous)
            with self.assertRaises(subprocess.CalledProcessError): run(root)
            self.assertEqual((root / 'data/site.json').read_bytes(),previous)
