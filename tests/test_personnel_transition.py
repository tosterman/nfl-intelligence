import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from personnel_changes import load_capture
from personnel_transition import build_transition

ROOT = Path(__file__).resolve().parents[1]


class PersonnelTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = ROOT / 'data/personnel-sources'
        cls.captures = sorted((load_capture(p, cls.folder) for p in cls.folder.glob('*.snapshot.json.gz')),
                              key=lambda c: c['retrievedAt'])

    def test_latest_pair_matches_existing_presentation_without_archive_scan(self):
        before, after = self.captures[-2:]
        with patch.object(Path, 'glob', side_effect=AssertionError('Cumulative scan')):
            result = build_transition(self.folder, after['captureHash'], before['captureHash'])
        expected = json.loads((ROOT / 'data/personnel-changes.json').read_bytes())
        self.assertEqual(result['presentation'], expected)
        self.assertEqual(result['beforeCapture'], before['captureHash'])

    def test_initial_capture_has_no_invented_comparison(self):
        result = build_transition(self.folder, self.captures[0]['captureHash'], None)
        self.assertIsNone(result['presentation']['previousRetrievedAt'])
        self.assertEqual(result['presentation']['changes'], [])

    def test_unchanged_or_reversed_captures_are_not_new_observations(self):
        first, last = self.captures[0]['captureHash'], self.captures[-1]['captureHash']
        for current, previous in [(last, last), (first, last)]:
            with self.assertRaises(ValueError):
                build_transition(self.folder, current, previous)

    def test_missing_or_invalid_capture_is_not_empty_history(self):
        for capture in ['../not-a-hash', '0' * 64]:
            with self.assertRaises((ValueError, FileNotFoundError)):
                build_transition(self.folder, capture, None)
