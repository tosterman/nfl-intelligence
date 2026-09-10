import sys,unittest,csv,gzip,hashlib,io,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from player_identity import compare_registry_ids

class PlayerIdentityTests(unittest.TestCase):
    def setUp(self):
        self.rows=[{'gsis_id':'current','display_name':'Same Name','esb_id':'explicit-alias','rookie_season':'2026'},
            {'gsis_id':'old','display_name':'Same Name','rookie_season':'1978'}]
    def test_equal_names_never_merge_distinct_registry_identifiers(self):
        self.assertEqual(compare_registry_ids(self.rows,'current','old')['status'],'different-registry-identities')
        self.assertEqual(compare_registry_ids(self.rows,'current','current')['status'],'same-registry-identity')
    def test_missing_or_different_namespace_id_stays_unresolved(self):
        for value in ['',None,'unknown','explicit-alias']:
            self.assertEqual(compare_registry_ids(self.rows,'current',value)['status'],'unresolved-registry')
    def test_duplicate_registry_ids_are_not_silently_selected(self):
        self.assertEqual(compare_registry_ids(self.rows+[self.rows[0]],'current','old')['status'],'ambiguous-registry')
    def test_archived_registry_reproduces_the_real_same_name_collision(self):
        root=Path(__file__).resolve().parents[1]
        source=json.loads((root/'reviews/player-registry-source.json').read_text())
        raw=gzip.decompress((root/'reviews/player-identity-source.csv.gz').read_bytes())
        self.assertEqual(len(raw),source['bytes']);self.assertEqual(hashlib.sha256(raw).hexdigest(),source['sha256'])
        result=compare_registry_ids(list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))),'00-0041363','THO581952')
        self.assertEqual(result['status'],'different-registry-identities')
        self.assertEqual((result['left'][0]['rookie_season'],result['right'][0]['last_season']),('2026','1978'))
        self.assertNotEqual(result['left'][0]['pfr_id'],result['right'][0]['pfr_id'])

if __name__=='__main__':unittest.main()
