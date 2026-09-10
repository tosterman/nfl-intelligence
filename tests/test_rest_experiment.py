import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import experiment_rest as rest

def game(date,home='PHI',away='DAL',season=2023):
    return {'game_id':date+'_'+away+'_'+home,'gameday':date,'home_team':home,'away_team':away,'season':season,'home_score':20,'away_score':10}

class RestEvidenceTests(unittest.TestCase):
    def test_future_and_cutoff_games_cannot_leak(self):
        target=game('2023-09-24');history=[game('2023-09-14','PHI','MIN'),game('2023-09-17','DAL','NYJ')]
        a=rest.rest_evidence(target,history,'2023-09-21')
        z=rest.rest_evidence(target,history+[game('2023-09-21'),game('2023-09-23'),game('2023-09-25')],'2023-09-21')
        self.assertEqual(a,z);self.assertEqual(a['difference'],3)

    def test_swap_negates_rest_correction(self):
        h=[game('2023-09-14','PHI','MIN'),game('2023-09-17','DAL','NYJ')]
        a=rest.rest_evidence(game('2023-09-24'),h,'2023-09-21')['difference']
        b=rest.rest_evidence(game('2023-09-24','DAL','PHI'),h,'2023-09-21')['difference']
        coefficient=rest.fit_rest(np.array([3.,-3.,0]),np.array([1.,-1.,50]),100)
        self.assertEqual(a,-b);self.assertEqual(a*coefficient,-b*coefficient)

    def test_opening_week_missing_not_offseason_rest(self):
        a=rest.rest_evidence(game('2023-09-10'),[game('2023-02-12',season=2022)],'2023-09-07')
        self.assertIsNone(a['difference']);self.assertIsNone(a['homeRestDays'])

    def test_uncompleted_rows_and_source_rest_fields_ignored(self):
        row=game('2023-09-24');row.update(home_rest=999,away_rest=1)
        prior=game('2023-09-17');prior['home_score']=None
        self.assertIsNone(rest.rest_evidence(row,[prior],'2023-09-21')['difference'])

    def test_future_residual_cannot_change_current_adjustment(self):
        rows=[game('2021-09-12','PHI','MIN',2021),game('2021-09-16','DAL','NYJ',2021),game('2021-09-26',season=2021),game('2021-10-03',season=2021)]
        records=[{'row':r,'cutoff':r['gameday'],'margin':2.,'total':40.} for r in rows]
        a=rest.corrected(records,rows,14,100)
        altered=[dict(p,row=dict(p['row'],home_score=999)) if p['row']['gameday']=='2021-10-03' else p for p in records]
        z=rest.corrected(altered,rows,14,100)
        self.assertEqual([p['adjustment'] for p in a[:-1]],[p['adjustment'] for p in z[:-1]])

if __name__=='__main__':unittest.main()
