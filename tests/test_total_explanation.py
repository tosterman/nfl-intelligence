import unittest
import numpy as np
from scripts.total_explanation import decompose


class TotalExplanation(unittest.TestCase):
    def fixture(self):
        rng = np.random.default_rng(51)
        score = rng.normal(size=66)
        score[0] = 22
        beta = rng.normal(size=(30, 2))
        beta[2:16, 1] = 0
        x = rng.normal(size=30)
        x[:2] = [1, 1]
        names = [f'feature {i}' for i in range(14)]
        return score, beta, x, names

    def test_matrix_total_reconciliation_swap_and_home_field_cancellation(self):
        score, beta, x, names = self.fixture()
        def vector(a, b, venue):
            v = np.zeros(66); v[0] = 1; v[1] = venue; v[2+a] = 1; v[34+b] = 1
            return v
        total = round(float(.75 * ((vector(2, 5, .5) + vector(5, 2, -.5)) @ score) + .25 * (x @ beta)[1]), 3)
        result = decompose(score, beta, x, 2, 5, names, total)
        self.assertAlmostEqual(sum(t['points'] for t in result['terms']), total, places=9)
        swapped = x.copy(); swapped[2:16] *= -1
        self.assertEqual(result, decompose(score, beta, swapped, 5, 2, names, total))
        score[1] += 100
        self.assertEqual(result, decompose(score, beta, x, 2, 5, names, total))
        x[1] = 0
        neutral_total = round(.75 * (2*score[0]+score[4]+score[7]+score[36]+score[39]) + .25*(x@beta)[1], 3)
        neutral = decompose(score, beta, x, 2, 5, names, neutral_total)
        self.assertEqual(next(t['points'] for t in neutral['terms'] if t['name'] == 'Efficiency venue'), 0)

    def test_invalid_design_or_mismatched_total_is_rejected(self):
        score, beta, x, names = self.fixture()
        with self.assertRaisesRegex(ValueError, 'reconcile'):
            decompose(score, beta, x, 2, 5, names, -999)
        beta[3, 1] = 1
        with self.assertRaisesRegex(ValueError, 'design'):
            decompose(score, beta, x, 2, 5, names, 40)
