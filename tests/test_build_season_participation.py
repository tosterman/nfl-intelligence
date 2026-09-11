import json
import hashlib
import gzip
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
            names = ['reviews/player-registry-source.json',
                     'reviews/player-identity-source.csv.gz','scripts/audit_personnel_identity.py']
            for name in names:
                target = root / name; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            # Freeze report scope and acquisition to this retained real source;
            # future production personnel refreshes must not alter this test.
            (root / 'data/participation-sources').mkdir(parents=True)
            source_bytes = (ROOT / 'reviews/player-usage-2026-source.csv.gz').read_bytes()
            source_hash = hashlib.sha256(gzip.decompress(source_bytes)).hexdigest()
            (root / f'data/participation-sources/{source_hash}.csv.gz').write_bytes(source_bytes)
            def save(name, value):
                (root / name).write_text(json.dumps(value), encoding='utf-8')
            at = '2026-09-11T16:00:00+00:00'
            player = {'playerId':'fixture-player','name':'Fixture Player','team':'SEA','season':2026,'type':'REG','week':1}
            players = [player, {**player,'playerId':'unresolved','name':'Unresolved Fixture'}]
            save('data/personnel.json', {'players':players,'sourceHash':'a'*64,'retrievedAt':at})
            save('data/quarterbacks.json', {})
            save('data/participation-source.json', {'status':'available','season':2026,'sourceHash':source_hash,'retrievedAt':at,
                'sourceUrl':'https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_2026.csv'})
            save('data/participation-collection.json', {'status':'collected','season':2026,'sourceHash':source_hash,'retrievedAt':at})
            (root / 'data/games.csv').write_text('game_id,season,week,game_type,gameday,gametime,home_team,away_team,home_score,away_score\n2026_01_NE_SEA,2026,1,REG,2026-09-09,20:20,SEA,NE,13,10\n')
            identity_rows = [{**p,'reportTeam':p['team'],'status':'matched' if i == 0 else 'identifier-mismatch'} for i,p in enumerate(players)]
            save('reviews/personnel-identity-audit.json', {'records':identity_rows,
                'inputHashes':{name:hashlib.sha256((root / f'data/{name}.json').read_bytes()).hexdigest() for name in ('personnel','quarterbacks')},
                'codeHash':hashlib.sha256((root / 'scripts/audit_personnel_identity.py').read_bytes()).hexdigest()})
            report = build(root)
            self.assertEqual(len(report['records']), 2)
            self.assertEqual(sum(r['identityStatus'] == 'matched' for r in report['records']), 1)
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
