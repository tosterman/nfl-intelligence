import sys
import unittest
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from replay_forecast import compare_prediction


class NumericalReplayTests(unittest.TestCase):
    def test_all_prediction_fields_and_training_metadata_are_checked(self):
        prediction = {'homeScore': 24.12, 'marginInterval80': [-10.0, 20.0],
                      'profiles': [{'team': 'LA', 'passEpa': .12}],
                      'contributions': [{'name': 'Home field', 'points': 0.0}]}
        snapshot = {'prediction': prediction, 'trainingGames': 100, 'trainingThrough': '2025-01-01'}
        self.assertTrue(compare_prediction(snapshot, prediction, 100, '2025-01-01'))
        for changed in [dict(prediction, homeScore=24.13), dict(prediction, extra=0),
                        dict(prediction, profiles=[]), dict(prediction, contributions=[]),
                        dict(prediction, marginInterval80=[-10, 21])]:
            self.assertFalse(compare_prediction(snapshot, changed, 100, '2025-01-01'))
        self.assertFalse(compare_prediction(snapshot, prediction, 101, '2025-01-01'))
        self.assertFalse(compare_prediction(snapshot, prediction, 100, '2025-01-02'))

    def test_booleans_cannot_impersonate_numbers(self):
        snapshot = {'prediction': {'homeScore': True}, 'trainingGames': 100, 'trainingThrough': '2025-01-01'}
        self.assertFalse(compare_prediction(snapshot, {'homeScore': 1.0}, 100, '2025-01-01'))
        snapshot['prediction'] = {'contributions': [{'points': False}]}
        self.assertFalse(compare_prediction(snapshot, {'contributions': [{'points': 0.0}]}, 100, '2025-01-01'))
        snapshot['prediction'] = {'homeScore': 1.0}
        self.assertTrue(compare_prediction(snapshot, {'homeScore': np.float64(1)}, 100, '2025-01-01'))
        snapshot['prediction'] = {'homeScore': float('nan')}
        self.assertFalse(compare_prediction(snapshot, snapshot['prediction'], 100, '2025-01-01'))
