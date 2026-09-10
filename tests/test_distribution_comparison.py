import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from compare_distributions import paired_weekly

def report(offset=0):
    return {'selected':'bw2','sources':[{'hash':'same'}],'selectedRecords':[
        {'gameId':f'2023_{week:02d}_A{game}_B','season':2023,'logScore':float(week)+offset}
        for week in [1,2,3] for game in range(week)]}

class ComparisonTests(unittest.TestCase):
    def test_constant_effect_is_exact_and_order_independent(self):
        a,b=report(),report(.25)
        result=paired_weekly(a,b,{2023},repetitions=1000)
        self.assertEqual(result['games'],6);self.assertEqual(result['weeks'],3)
        self.assertEqual(result['meanDifference'],.25)
        self.assertEqual(result['interval95'],[.25,.25])
        b['selectedRecords'].reverse()
        self.assertEqual(result,paired_weekly(a,b,{2023},repetitions=1000))

    def test_mismatch_duplicate_nonfinite_and_missing_season_fail(self):
        for mutation in ['source','missing','duplicate','nonfinite','season','candidate']:
            b=report()
            if mutation=='source':b['sources']=[]
            if mutation=='missing':b['selectedRecords'].pop()
            if mutation=='duplicate':b['selectedRecords'].append(b['selectedRecords'][0])
            if mutation=='nonfinite':b['selectedRecords'][0]['logScore']=float('nan')
            if mutation=='season':b['selectedRecords'][0]['season']=2022
            if mutation=='candidate':b['selected']='different'
            with self.assertRaises(ValueError):paired_weekly(report(),b,{2023})
        with self.assertRaises(ValueError):paired_weekly(report(),report(),{2020})

    def test_game_weighting_not_unweighted_week_means(self):
        b=report()
        for r in b['selectedRecords']:r['logScore']+=int(r['gameId'].split('_')[1])
        result=paired_weekly(report(),b,{2023},repetitions=1000)
        self.assertAlmostEqual(result['meanDifference'],14/6)
        self.assertGreater(result['interval95'][1],result['interval95'][0])
        self.assertEqual(result,paired_weekly(report(),b,{2023},repetitions=1000))

if __name__=='__main__':unittest.main()
