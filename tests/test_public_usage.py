import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_public_usage import build_payload


def fixture():
    player = dict(playerId='id', name='Player', team='PHI', season=2026, type='REG', week=1)
    personnel = dict(sourceHash='source', retrievedAt='2026-09-10T10:00:00Z', players=[player])
    usage = dict(personnelArtifactHash='hash', sourceSeason=2025, generatedAt='2026-09-10T11:00:00Z',
                 snapSourceHash='snap', registrySourceHash='registry', records=[dict(player, usage={'status':'unavailable','reason':'No eligible historical appearances'})])
    identity = dict(inputHashes={'personnel':'hash'}, records=[dict(player, reportTeam='PHI', status='matched')])
    return personnel, usage, identity


class PublicUsageTests(unittest.TestCase):
    def test_unknown_stays_unknown_and_input_binding_is_retained(self):
        p,u,i=fixture();out=build_payload(p,u,i,'hash')
        self.assertEqual(out['records'][0]['usage']['status'],'unavailable')
        self.assertNotIn('weightedShares',out['records'][0]['usage'])
        self.assertEqual(out['personnelRetrievedAt'],p['retrievedAt'])

    def test_old_audit_duplicate_and_mismatched_name_are_rejected(self):
        for kind in ['usage-hash','identity-hash','duplicate','name']:
            p,u,i=fixture()
            if kind=='usage-hash':u['personnelArtifactHash']='old'
            if kind=='identity-hash':i['inputHashes']['personnel']='old'
            if kind=='duplicate':u['records']*=2
            if kind=='name':u['records'][0]['name']='Different'
            with self.subTest(kind=kind),self.assertRaises(ValueError):build_payload(p,u,i,'hash')

    def test_identity_conflicts_do_not_publish_usage(self):
        p,u,i=fixture();i['records'][0]['status']='identifier-mismatch'
        u['records'][0]['usage']={'status':'available','weightedShares':{'defense_pct':1}}
        result=build_payload(p,u,i,'hash')['records'][0]['usage']
        self.assertEqual(result,{'status':'unavailable','reason':'Historical identity not corroborated'})

if __name__=='__main__':unittest.main()
