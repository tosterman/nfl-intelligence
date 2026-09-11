import gzip
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from weather_bundle import ROOT, encode, fingerprint
from weather_partitions import build_partitions, verify_migration


class WeatherPartitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build_partitions(ROOT)

    def test_every_observation_and_source_survives_exactly(self):
        result = self.result
        summary = verify_migration(ROOT, result)
        ledger = json.loads((ROOT / 'data/weather-ledger.json').read_bytes())
        self.assertEqual(summary['observations'], len(ledger))
        self.assertEqual(summary['games'], len({row['gameId'] for row in ledger}))
        publication = json.loads(result['objects'][result['publication']['sha256']])
        index = json.loads(result['objects'][publication['index']['sha256']])
        actual = []
        for game, ref in index['games'].items():
            partition = json.loads(result['objects'][ref['sha256']])
            rows = json.loads(partition['ledgerJson'])
            self.assertTrue(all(row['gameId'] == game for row in rows))
            actual.extend(rows)
            for source_hash, source_ref in partition['sources'].items():
                self.assertEqual(gzip.decompress(result['objects'][source_ref['sha256']]),
                                 gzip.decompress((ROOT / 'data/weather-sources' / (source_hash + '.json.gz')).read_bytes()))
        self.assertEqual(sorted(actual, key=lambda r: r['hash']), sorted(ledger, key=lambda r: r['hash']))
        self.assertEqual(result, build_partitions(ROOT))

    def test_missing_or_corrupt_objects_fail_migration_audit(self):
        ref = self.result['publication']['sha256']
        for body in [None, b'{}']:
            changed = {**self.result, 'objects': dict(self.result['objects'])}
            if body is None:
                del changed['objects'][ref]
            else:
                changed['objects'][ref] = body
            with self.assertRaises(ValueError):
                verify_migration(ROOT, changed)

    def test_rehashed_index_cannot_drop_a_game(self):
        changed = {**self.result, 'objects': dict(self.result['objects'])}
        publication = json.loads(changed['objects'][changed['publication']['sha256']])
        index = json.loads(changed['objects'][publication['index']['sha256']])
        del index['games'][next(iter(index['games']))]
        raw = encode(index); identity = fingerprint(index)
        changed['objects'][identity] = raw
        publication['index'] = {'sha256': identity, 'bytes': len(raw)}
        raw = encode(publication); identity = fingerprint(publication)
        changed['objects'][identity] = raw
        changed['publication'] = {'sha256': identity, 'bytes': len(raw)}
        with self.assertRaisesRegex(ValueError, 'game|observation|migration'):
            verify_migration(ROOT, changed)

    def test_rehashed_partition_cannot_remove_an_observation(self):
        changed = {**self.result, 'objects': dict(self.result['objects'])}
        publication = json.loads(changed['objects'][changed['publication']['sha256']])
        index = json.loads(changed['objects'][publication['index']['sha256']])
        game = next(iter(index['games']))
        partition = json.loads(changed['objects'][index['games'][game]['sha256']])
        rows = json.loads(partition['ledgerJson'])
        partition['ledgerJson'] = encode(rows[1:]).decode()
        def retain(value):
            raw = encode(value); identity = fingerprint(value)
            changed['objects'][identity] = raw
            return {'sha256': identity, 'bytes': len(raw)}
        index['games'][game] = retain(partition)
        publication['index'] = retain(index)
        changed['publication'] = retain(publication)
        with self.assertRaisesRegex(ValueError, 'observations'):
            verify_migration(ROOT, changed)


if __name__ == '__main__':
    unittest.main()
