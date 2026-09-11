import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from replay_personnel_candidate import verify_output,validate_degraded_report


class PersonnelReplayTests(unittest.TestCase):
    def test_degraded_report_requires_ordered_failed_attempt(self):
        valid={'derivationFailure':'historical-usage','derivations':[
            {'step':'audit_personnel_identity.py','exitCode':0},
            {'step':'audit_player_usage.py','exitCode':124}]}
        self.assertEqual(validate_degraded_report(valid),'historical-usage')
        for invalid in ({**valid,'derivationFailure':'identity-audit'},
                        {**valid,'derivations':valid['derivations'][1:]},
                        {**valid,'derivations':[{'step':'audit_personnel_identity.py','exitCode':True}]},
                        {**valid,'derivations':[]}):
            with self.assertRaises(ValueError):validate_degraded_report(invalid)

    def test_json_transport_line_endings_do_not_change_computed_evidence(self):
        verify_output(b'{\n"value": 1\n}\n', b'{\r\n"value": 1\r\n}\r\n')

    def test_changed_evidence_and_numeric_types_are_rejected(self):
        for changed in (b'{"value":2}',b'{"value":true}',b'{"value":1.0}'):
            with self.assertRaises(ValueError):
                verify_output(changed,b'{"value":1}')
