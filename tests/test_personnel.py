import csv, gzip, hashlib, io, json, sys, unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from refresh_personnel import normalize, for_game

class PersonnelTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(season='2026', game_type='REG', team='CHI', week='1', gsis_id='00-0030000', full_name='Example Player', position='QB', report_status='', practice_status='Limited Participation in Practice')
        self.now = datetime(2026, 9, 10, 12, tzinfo=timezone.utc)
        self.game = dict(season=2026, type='REG', week=1, home='CAR', away='CHI', kickoff=(self.now + timedelta(days=2)).isoformat())

    def raw(self, rows):
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=list(self.row))
        writer.writeheader(); writer.writerows(rows)
        return out.getvalue().encode()

    def snapshot(self):
        return dict(status='available', retrievedAt=self.now.isoformat(), assetUpdatedAt=self.now.isoformat(), players=normalize(self.raw([self.row]), 2026, {'CHI', 'CAR'}))

    def test_blank_report_is_unknown_and_missing_team_is_not_healthy(self):
        result = for_game(self.snapshot(), self.game, self.now)
        self.assertIsNone(result['players'][0]['reportStatus'])
        self.assertEqual(result['teamsWithoutRows'], ['CAR'])

    def test_reject_scope_duplicate_and_status_ambiguity(self):
        for changes in [{'season':'2025'}, {'team':'XXX'}, {'week':'0'}, {'game_type':'PRE'}, {'gsis_id':''}, {'report_status':'Healthy'}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                normalize(self.raw([self.row | changes]), 2026, {'CHI'})
        with self.assertRaises(ValueError):
            normalize(self.raw([self.row, self.row]), 2026, {'CHI'})

    def test_exact_game_scope(self):
        for changes in [{'season':2025}, {'type':'POST'}, {'week':2}, {'away':'DEN'}]:
            self.assertEqual(for_game(self.snapshot(), self.game | changes, self.now)['players'], [])

    def test_old_source_cannot_be_made_fresh_by_redownload(self):
        snap = self.snapshot()
        snap['assetUpdatedAt'] = (self.now - timedelta(hours=31)).isoformat()
        self.assertEqual(for_game(snap, self.game, self.now)['status'], 'unavailable')

    def test_postseason_schedule_phases_match_post_reports(self):
        for phase, week in [('WC', 19), ('DIV', 20), ('CON', 21), ('SB', 22)]:
            snap = self.snapshot()
            snap['players'][0].update(type='POST', week=week)
            self.assertEqual(len(for_game(snap, self.game | {'type': phase, 'week': week}, self.now)['players']), 1)
            self.assertEqual(for_game(snap, self.game | {'type': 'REG', 'week': week}, self.now)['players'], [])

    def test_postgame_and_future_snapshots_are_withheld(self):
        snap = self.snapshot()
        self.assertEqual(for_game(snap, self.game, self.now + timedelta(days=3))['status'], 'unavailable')
        self.assertEqual(for_game(snap, self.game | {'status': 'final'}, self.now)['status'], 'unavailable')
        snap['retrievedAt'] = (self.now + timedelta(seconds=1)).isoformat()
        self.assertEqual(for_game(snap, self.game, self.now)['status'], 'unavailable')

    def test_captured_source_and_snapshot_are_reproducible(self):
        root = Path(__file__).resolve().parents[1]
        snapshot = json.loads((root / 'data/personnel.json').read_text())
        raw = gzip.decompress((root / 'data/personnel-sources' / (snapshot['sourceHash'] + '.csv.gz')).read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), snapshot['sourceHash'])
        site = json.loads((root / 'data/site.json').read_text())
        teams = {g[side] for g in site['games'] for side in ('home', 'away')}
        self.assertEqual(normalize(raw, snapshot['season'], teams), snapshot['players'])
        for path in (root / 'data/personnel-sources').glob('*.snapshot.json.gz'):
            captured = gzip.decompress(path.read_bytes())
            self.assertEqual(hashlib.sha256(captured).hexdigest(), path.name.split('.')[0])

if __name__ == '__main__':
    unittest.main()
