import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from weather_history import build, verify_record


class WeatherHistory(unittest.TestCase):
    def test_complete_retained_replay(self):
        report = build(ROOT)
        self.assertEqual(report, json.loads((ROOT / 'data/weather-history.json').read_text()))
        self.assertGreater(len(report['records']), 0)

    def test_tampered_observation_and_rehashed_measurements_rejected(self):
        record = json.loads((ROOT / 'data/weather-ledger.json').read_text())[0]
        changed = copy.deepcopy(record)
        changed['temperature'] += 1
        with self.assertRaisesRegex(ValueError, 'fingerprint'):
            verify_record(changed, ROOT)
        changed['hash'] = hashlib.sha256(json.dumps({k:v for k,v in changed.items() if k != 'hash'}, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'retained response'):
            verify_record(changed, ROOT)

    def test_source_fingerprint_rejected(self):
        record = json.loads((ROOT / 'data/weather-ledger.json').read_text())[0]
        with patch('weather_history.gzip.decompress', return_value=b'{}'):
            with self.assertRaisesRegex(ValueError, 'source fingerprint'):
                verify_record(record, ROOT)
