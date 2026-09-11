import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_season_participation import ROOT, build


class SeasonParticipationBinding(unittest.TestCase):
    def test_real_scope_identity_failure_and_retained_source_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = ['data/personnel.json','data/quarterbacks.json','data/games.csv',
                     'data/participation-source.json','data/participation-collection.json',
                     'reviews/personnel-identity-audit.json','reviews/player-registry-source.json',
                     'reviews/player-identity-source.csv.gz','scripts/audit_personnel_identity.py']
            for name in names:
                target = root / name; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            shutil.copytree(ROOT / 'data/participation-sources', root / 'data/participation-sources')
            report = build(root)
            self.assertEqual(len(report['records']), 139)
            self.assertEqual(sum(r['identityStatus'] == 'matched' for r in report['records']), 134)
            self.assertTrue(all(r['usage'] is None or r['usage']['overall']['status'] == 'unavailable' for r in report['records']))
            self.assertTrue(all(r['usage'] is None for r in report['records'] if r['identityStatus'] != 'matched'))
            (root / 'data/participation-collection.json').write_text(json.dumps({'status': 'failed'}))
            retained = build(root)
            self.assertEqual(retained['collectionStatus'], 'retained')
            self.assertEqual(retained['sourceRetrievedAt'], report['sourceRetrievedAt'])
            self.assertEqual(retained['records'], report['records'])
            identity_path = root / 'reviews/personnel-identity-audit.json'
            identity = json.loads(identity_path.read_text()); identity['inputHashes']['personnel'] = 'wrong'
            identity_path.write_text(json.dumps(identity))
            with self.assertRaisesRegex(ValueError, 'Identity audit does not match'):
                build(root)
