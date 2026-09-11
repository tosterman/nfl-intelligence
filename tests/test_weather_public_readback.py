import sys
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_weather_publication import verify


class WeatherReadbackTests(unittest.TestCase):
    def test_exact_bundle_and_freshness_are_both_required(self):
        now = datetime(2026, 9, 11, 18, tzinfo=timezone.utc)
        at = now.isoformat()
        receipt = {'mode': 'published', 'manifestHash': 'a' * 64, 'generatedAt': at}
        payload = {'status': 'ok', 'manifestHash': 'a' * 64, 'generatedAt': at,
                   'collectionStartedAt': at, 'maximumAgeHours': 30,
                   'eligibleGames': 1, 'availableGames': 1,
                   'checks': [{'gameId': 'game', 'status': 'ok', 'issuedAt': at,
                               'retrievedAt': at, 'sourceHash': 'b' * 64}]}
        verify(receipt, 200, payload, now)
        for change in [{'manifestHash': 'c' * 64}, {'availableGames': 0},
                       {'generatedAt': (now - timedelta(minutes=1)).isoformat()},
                       {'checks': [{**payload['checks'][0], 'issuedAt': (now - timedelta(hours=31)).isoformat()}]}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify(receipt, 200, {**payload, **change}, now)
        with self.assertRaises(ValueError):
            verify({**receipt, 'mode': 'read-only-rehearsal'}, 200, payload, now)
        with self.assertRaises(ValueError):
            verify(receipt, 503, payload, now)


if __name__ == '__main__':
    unittest.main()
