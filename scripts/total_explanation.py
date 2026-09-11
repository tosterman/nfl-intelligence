"""Additive total accounting for the fixed 75/25 model; not a new predictor.

Caller must first verify source/code identities and reproduce the full archived
prediction. This pure accounting function alone does not authorize UI display.
"""
import math
import numpy as np


def decompose(score_beta, efficiency_beta, features, home_index, away_index, names, expected_total):
    score = np.asarray(score_beta, dtype=float)
    efficiency = np.asarray(efficiency_beta, dtype=float)
    x = np.asarray(features, dtype=float)
    if score.shape != (66,) or efficiency.shape != (30, 2) or x.shape != (30,):
        raise ValueError('Unsupported coefficient or feature shape')
    if any(type(i) is not int or not 0 <= i < 32 for i in (home_index, away_index)) or home_index == away_index:
        raise ValueError('Invalid team indices')
    if len(names) != 14 or len(set(names)) != 14 or not all(isinstance(n, str) and n for n in names):
        raise ValueError('Expected fourteen unique summed-feature names')
    if not all(np.isfinite(v).all() for v in (score, efficiency, x)) or not math.isfinite(expected_total):
        raise ValueError('Nonfinite total accounting inputs')
    if x[0] != 1 or x[1] not in (0, 1) or np.any(efficiency[2:16, 1] != 0):
        raise ValueError('Unsupported total design')
    terms = [
        ('Scoring baseline', .75 * 2 * score[0]),
        ('Scoring offense', .75 * (score[2 + home_index] + score[2 + away_index])),
        ('Scoring defense', .75 * (score[34 + home_index] + score[34 + away_index])),
        ('Efficiency intercept', .25 * efficiency[0, 1]),
        ('Efficiency venue', .25 * x[1] * efficiency[1, 1]),
    ] + [(f'Efficiency sum: {name}', .25 * x[16 + i] * efficiency[16 + i, 1]) for i, name in enumerate(names)]
    total = math.fsum(float(value) for _, value in terms)
    if round(total, 3) != expected_total:
        raise ValueError('Explanation does not reconcile to the published total')
    displayed = [{'name': name, 'points': round(float(value), 3)} for name, value in terms]
    residual = round(expected_total - math.fsum(t['points'] for t in displayed), 3)
    if residual:
        displayed.append({'name': 'Rounding reconciliation', 'points': residual})
    return {'schemaVersion': 1, 'total': expected_total, 'unroundedTotal': total,
            'terms': displayed, 'rawTerms': [{'name': name, 'points': float(value)} for name, value in terms],
            'limitations': 'Additive model accounting, not causal effects. The efficiency intercept is not average league scoring.'}
