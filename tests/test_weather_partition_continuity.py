import copy
import json
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from weather_bundle import ROOT, encode, fingerprint
from weather_partitions import build_partitions, digest, verify_partition_continuity


class PartitionContinuityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = build_partitions(ROOT)

    def rewrite(self, mutation):
        result = copy.deepcopy(self.original)
        def retain(value):
            raw = encode(value); identity = digest(raw)
            result['objects'][identity] = raw
            return {'sha256': identity, 'bytes': len(raw)}
        publication = json.loads(result['objects'][result['publication']['sha256']])
        publication['generatedAt'] = (datetime.fromisoformat(publication['generatedAt']) + timedelta(minutes=1)).isoformat()
        index = json.loads(result['objects'][publication['index']['sha256']])
        game = next(iter(index['games']))
        partition = json.loads(result['objects'][index['games'][game]['sha256']])
        mutation(index, game, partition, publication)
        if game in index['games']:
            index['games'][game] = retain(partition)
        publication['index'] = retain(index)
        result['publication'] = retain(publication)
        return result

    def test_unchanged_partitions_require_no_history_download(self):
        root = json.loads(self.original['objects'][self.original['publication']['sha256']])
        refs = [self.original['publication']['sha256'], root['index']['sha256']]
        scoped = {**self.original, 'objects': {key: self.original['objects'][key] for key in refs}}
        self.assertEqual(verify_partition_continuity(scoped, scoped)['changedGames'], 0)

    def test_appending_an_observation_preserves_prior_rows(self):
        def append(index, game, partition, root):
            rows = json.loads(partition['ledgerJson'])
            row = {key: value for key, value in rows[0].items() if key != 'hash'}
            row['retrievedAt'] = (datetime.fromisoformat(row['retrievedAt']) + timedelta(seconds=1)).isoformat()
            row['hash'] = fingerprint(row)
            compact = {**partition['history']['records'][0], 'retrievedAt': row['retrievedAt'], 'hash': row['hash']}
            rows.append(row); partition['ledgerJson'] = encode(rows).decode()
            partition['history']['records'].append(compact)
        self.assertEqual(verify_partition_continuity(self.original, self.rewrite(append))['changedGames'], 1)

    def test_game_observation_and_source_removal_are_rejected(self):
        def remove_row(index, game, partition, root):
            rows = json.loads(partition['ledgerJson']); partition['ledgerJson'] = encode(rows[1:]).decode()
        def change_row(index, game, partition, root):
            rows = json.loads(partition['ledgerJson']); rows[0]['temperature'] = 999
            partition['ledgerJson'] = encode(rows).decode()
        def remove_source(index, game, partition, root):
            del partition['sources'][next(iter(partition['sources']))]
        for mutation in [lambda index, game, partition, root: index['games'].pop(game), remove_row, change_row, remove_source]:
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                verify_partition_continuity(self.original, self.rewrite(mutation))

    def test_earlier_or_conflicting_same_time_publication_is_rejected(self):
        earlier = self.rewrite(lambda index, game, partition, root: root.update(generatedAt='2000-01-01T00:00:00Z'))
        with self.assertRaises(ValueError):
            verify_partition_continuity(self.original, earlier)
        original_time = json.loads(self.original['objects'][self.original['publication']['sha256']])['generatedAt']
        changed = self.rewrite(lambda index, game, partition, root: root.update(generatedAt=original_time, extra='conflict'))
        with self.assertRaises(ValueError):
            verify_partition_continuity(self.original, changed)


if __name__ == '__main__':
    unittest.main()
