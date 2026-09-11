import copy
import gzip
import hashlib
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from personnel_presentation import assemble, FILES

ROOT = Path(__file__).resolve().parents[1]


class PersonnelPresentationTests(unittest.TestCase):
    def setUp(self):
        self.files = {name: (ROOT / 'data' / name).read_bytes() for name in FILES}
        audit = (ROOT / 'reviews/personnel-identity-audit.json').read_bytes()
        expected = json.loads(self.files['player-usage.json'])['auditHashes']['identity']
        # This retained fixture was produced on Windows before Git normalized
        # the audit's line endings. Reconstruct only if its declared hash proves
        # those exact original bytes; production validation remains exact.
        if hashlib.sha256(audit).hexdigest() != expected:
            audit = audit.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
        self.assertEqual(hashlib.sha256(audit).hexdigest(), expected)
        self.files['identityAudit'] = audit
        site = json.loads(self.files['site.json'])
        self.files['games.csv'] = gzip.decompress((ROOT / 'data/forecast-input-archive/objects' / (site['source']['sha256']+'.gz')).read_bytes())

    def change(self, name, **fields):
        value = json.loads(self.files[name])
        value.update(fields)
        self.files[name] = json.dumps(value).encode()

    def test_current_set_is_bound_and_does_not_mutate_inputs(self):
        before = copy.deepcopy(self.files)
        value = assemble(self.files)
        self.assertEqual(value['derivation']['status'], 'compatible')
        self.assertEqual(len(value['contexts']), len(json.loads(self.files['site.json'])['games']))
        self.assertIsNotNone(value['evidence']['current'])
        self.assertEqual(self.files, before)

    def test_mixed_derived_artifact_is_rejected(self):
        for name in ('player-usage.json', 'season-participation.json'):
            original = self.files[name]
            self.change(name, personnelSourceHash='0'*64)
            with self.assertRaisesRegex(ValueError, 'participation binding'):
                assemble(self.files)
            self.files[name] = original

    def test_incompatible_cutoff_withholds_usage_and_preserves_failure(self):
        now = datetime.now(timezone.utc).isoformat()
        self.change('personnel.json', retrievedAt=now, assetUpdatedAt=now)
        self.change('personnel-changes.json', retrievedAt=now)
        self.change('quarterback-collection.json', status='unavailable')
        result = assemble(self.files)
        self.assertEqual(result['derivation']['status'], 'unavailable')
        self.assertIsNone(result['evidence']['historical'])
        self.assertIsNone(result['evidence']['current'])
        self.assertEqual(result['evidence']['quarterbackCollection']['status'], 'unavailable')
        self.assertEqual(result['evidence']['quarterback'], json.loads(self.files['quarterbacks.json']))

    def test_future_dates_and_mixed_history_are_rejected(self):
        original = self.files['quarterbacks.json']
        self.change('quarterbacks.json', retrievedAt='2199-01-01T00:00:00Z')
        with self.assertRaisesRegex(ValueError, 'chronology'):
            assemble(self.files)
        self.files['quarterbacks.json'] = original
        self.change('personnel-changes.json', sourceHash='0'*64)
        with self.assertRaisesRegex(ValueError, 'history binding'):
            assemble(self.files)

    def test_failed_participation_is_labeled_retained_without_changing_source_dates(self):
        original = json.loads(self.files['season-participation.json'])
        self.change('participation-collection.json', status='failed')
        current = assemble(self.files)['evidence']['current']
        self.assertEqual(current['collectionStatus'], 'retained')
        self.assertEqual(current['sourceRetrievedAt'], original['sourceRetrievedAt'])

    def test_replaced_quarterback_evidence_cannot_reuse_previous_usage(self):
        self.change('quarterbacks.json', sourceHash='0'*64)
        with self.assertRaisesRegex(ValueError, 'identity audit binding'):
            assemble(self.files)

    def test_derivation_failure_preserves_reports_dates_and_collection_failure(self):
        self.change('participation-collection.json', status='failed')
        before=copy.deepcopy(self.files)
        self.files['player-usage.json']=b'truncated output'
        self.files['season-participation.json']=b'truncated output'
        expected=copy.deepcopy(self.files)
        for failure in ('identity-audit','historical-usage','current-participation'):
            value=assemble(self.files,derivation_failure=failure)
            self.assertIsNone(value['evidence']['historical'])
            self.assertIsNone(value['evidence']['current'])
            self.assertEqual(value['evidence']['snapshot'],json.loads(before['personnel.json']))
            self.assertEqual(value['evidence']['participationCollection']['status'],'failed')
            self.assertEqual(value['derivation']['status'],'unavailable')
        self.assertEqual(self.files,expected)

    def test_degraded_derivation_cannot_bypass_source_history_or_schedule_checks(self):
        with self.assertRaisesRegex(ValueError,'Unknown'):
            assemble(self.files,derivation_failure='anything')
        self.change('personnel-changes.json',sourceHash='0'*64)
        with self.assertRaisesRegex(ValueError,'history binding'):
            assemble(self.files,derivation_failure='identity-audit')
