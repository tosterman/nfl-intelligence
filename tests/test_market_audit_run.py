import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_market_audit as audit

class MarketAuditFailureTests(unittest.TestCase):
    def test_export_and_report_failure_leave_sanitized_current_outcome(self):
        for stage in ['export','report']:
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as folder:
                root=Path(folder);recovery=root/'release-recovery';recovery.mkdir()
                (recovery/'market-audit-retention.json').write_text('{"old":true}')
                error=subprocess.CalledProcessError(1,['secret-command'],stderr='secret provider body')
                outcomes=[error] if stage=='export' else [SimpleNamespace(stdout='{"folder":"export"}'),error]
                with patch.object(audit,'ROOT',root),patch.object(audit.subprocess,'run',side_effect=outcomes):
                    with self.assertRaises(subprocess.CalledProcessError):audit.main()
                raw=(recovery/'market-audit-run.json').read_text();state=json.loads(raw)
                self.assertFalse(state['success']);self.assertEqual(state['stage'],stage)
                self.assertNotIn('secret',raw)
                self.assertFalse((recovery/'market-audit-retention.json').exists())
                self.assertLessEqual(state['startedAt'],state['completedAt'])
