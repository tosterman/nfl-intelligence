import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_total_explanations import compare


class VerifyTotalExplanations(unittest.TestCase):
    def test_changed_display_provenance_and_raw_terms_fail(self):
        saved = json.loads((Path(__file__).resolve().parents[1] / 'data/total-explanations.json').read_text())
        compare(saved, saved)
        identity = next(iter(saved['records']))
        for mode in ('term', 'coverage', 'engine', 'raw'):
            changed = copy.deepcopy(saved)
            if mode == 'term': changed['records'][identity]['terms'][0]['points'] += .001
            if mode == 'coverage': del changed['records'][identity]
            if mode == 'engine': changed['modelCodeHash'] = 'other'
            if mode == 'raw': changed['records'][identity]['rawTerms'][0]['points'] += .0001
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                compare(changed, saved)
        tiny = copy.deepcopy(saved)
        tiny['records'][identity]['rawTerms'][0]['points'] += 1e-11
        compare(tiny, saved)
