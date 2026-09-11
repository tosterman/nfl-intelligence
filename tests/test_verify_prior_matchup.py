import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.refresh_weekly_matchup import encode
from scripts.verify_prior_matchup import verify


class VerifyPrior(unittest.TestCase):
    def test_success_fallback_tamper_and_interrupted_update(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / 'data/weekly-matchup-sources'
            archive.mkdir(parents=True)
            sample = {'forecastSeason': 2026, 'count': 1}
            digest = hashlib.sha256(encode(sample)).hexdigest()
            manifest = {'plays': {'sha256': 'source'}}
            identity = hashlib.sha256(encode(manifest)).hexdigest()
            receipt = {'status': 'ok', 'forecastSeason': 2026, 'artifactSha256': digest, 'manifestHash': identity}
            (archive / f'{digest}.snapshot.json').write_bytes(encode(sample))
            (archive / f'{identity}.manifest.json').write_bytes(encode(manifest))
            (archive / f'{hashlib.sha256(encode(receipt)).hexdigest()}.snapshot.json').write_bytes(encode(receipt))
            current = root / 'data/prior-matchup-context.json'
            collection = root / 'data/prior-matchup-collection.json'
            current.write_bytes(encode(sample))
            collection.write_bytes(encode(receipt))
            (root / 'data/red-zone-adjudications.json').write_text('{"sourceSha256":"source","decisions":[]}')
            with patch('scripts.verify_prior_matchup.from_retained', return_value=sample):
                self.assertEqual(verify(root), digest)
                collection.write_text('{"status":"unavailable"}')
                self.assertEqual(verify(root), digest)
                changed = {**sample, 'count': 2}
                changed_digest = hashlib.sha256(encode(changed)).hexdigest()
                (archive / f'{changed_digest}.snapshot.json').write_bytes(encode(changed))
                current.write_bytes(encode(changed))
                with self.assertRaisesRegex(ValueError, 'No successful receipt'):
                    verify(root)
                collection.write_bytes(encode(receipt))
                with self.assertRaisesRegex(ValueError, 'disagree'):
                    verify(root)
                current.write_bytes(encode(sample))
            with patch('scripts.verify_prior_matchup.from_retained', return_value={'changed': True}):
                with self.assertRaisesRegex(ValueError, 'does not replay'):
                    verify(root)
