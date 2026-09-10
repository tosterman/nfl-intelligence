import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from production_health import edition_parity,health_evidence
class EditionParityTests(unittest.TestCase):
    def setUp(self):
        self.expected={'generatedAt':'2026-09-10T20:10:00Z','modelVersion':'v1','source':{'sha256':'a'*64}}
        self.observed={'generatedAt':'2026-09-10T20:10:00+00:00','modelVersion':'v1','sourceHash':'a'*64}
    def test_exact_identity_and_equivalent_timestamp(self):
        self.assertEqual(edition_parity(self.expected,self.observed)['status'],'matching')
    def test_fresh_but_older_and_changed_identity_are_distinct(self):
        self.assertEqual(edition_parity(self.expected,self.observed|{'generatedAt':'2026-09-10T20:09:00Z'})['status'],'behind-intended')
        for patch in [{'sourceHash':'b'*64},{'modelVersion':'v2'},{'generatedAt':'2026-09-10T20:11:00Z'}]:
            self.assertEqual(edition_parity(self.expected,self.observed|patch)['status'],'different-identity')
    def test_missing_identity_never_matches(self):
        for expected,observed in [({},self.observed),(self.expected,None),(self.expected,{}),(self.expected|{'generatedAt':'invalid'},self.observed)]:
            self.assertEqual(edition_parity(expected,observed)['status'],'unverified')
    def test_health_evidence_excludes_unexpected_payload_fields(self):
        self.assertEqual(health_evidence('forecasts',self.observed|{'secret':'do-not-retain','rawResponse':'private'}),self.observed)
