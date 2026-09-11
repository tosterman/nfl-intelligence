import hashlib
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from source_record_changes import compare_csv


def compare(before, after, keys=('game_id',)):
    return compare_csv(before, after, hashlib.sha256(before).hexdigest(),
                       hashlib.sha256(after).hexdigest(), keys)


class SourceRecordChangesTests(unittest.TestCase):
    def test_new_removed_and_revised_rows_are_separate(self):
        result = compare(b'game_id,score\na,10\nb,7\n', b'game_id,score\na,13\nc,0\n')
        self.assertEqual(result['added'], [{'key': ['c'], 'record': {'game_id': 'c', 'score': '0'}}])
        self.assertEqual(result['removed'][0]['key'], ['b'])
        self.assertEqual(result['revised'], [{'key': ['a'], 'fields': {'score': {'before': '10', 'after': '13'}}}])

    def test_byte_change_can_have_no_record_change(self):
        result = compare(b'game_id,score\na,10\nb,7\n', b'score,game_id\r\n7,b\r\n10,a\r\n')
        self.assertTrue(result['bytesChanged'])
        self.assertFalse(result['recordsChanged'])

    def test_untrusted_identity_schema_and_hash_are_rejected(self):
        good = b'game_id,team,score\na,DET,7\n'
        for bad in [b'game_id,team,score\na,DET,7\na,DET,8\n',
                    b'game_id,team,score\n,DET,7\n', b'game_id,team,score\na,,7\n',
                    b'game_id,team,team\na,DET,DET\n', b'game_id,team,score\na,DET\n',
                    b'game_id,team,score\na,DET,7,extra\n']:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                compare(good, bad, ('game_id', 'team'))
        with self.assertRaises(ValueError):
            compare_csv(good, good, '0' * 64, hashlib.sha256(good).hexdigest(), ('game_id',))
        with self.assertRaises(ValueError):
            compare(good, b'game_id,team,points\na,DET,7\n')


if __name__ == '__main__':
    unittest.main()
