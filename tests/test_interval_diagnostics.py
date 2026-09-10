import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from interval_diagnostics import summarize,audit

class IntervalDiagnosticsTests(unittest.TestCase):
    def test_fixed_boundaries_and_missing_markets_partition_records(self):
        base={'marginInterval80':[-10,10],'actualMargin':0,'totalInterval80':[30,60],'actualTotal':45,'homeMargin':6,'marketMargin':0}
        rows=[base|{'id':'a','homeWinProbability':.6},base|{'id':'b','homeWinProbability':.8,'marketMargin':None}]
        result=audit(rows)
        self.assertEqual([g['margin']['games'] for g in result['confidence']],[0,1,0,1])
        self.assertEqual([g['margin']['games'] for g in result['disagreement']],[0,0,0,1])
        self.assertEqual(result['missingMarketGames'],1)
    def test_coverage_tail_direction_width_and_miss_penalty(self):
        rows=[{'id':'a','marginInterval80':[-10,10],'actualMargin':20},
              {'id':'b','marginInterval80':[-10,10],'actualMargin':0},
              {'id':'c','marginInterval80':[-10,10],'actualMargin':-10}]
        r=summarize(rows,'marginInterval80','actualMargin')
        self.assertEqual((r['games'],r['covered'],r['below'],r['above']),(3,2,0,1))
        self.assertEqual(r['meanWidth'],20)
        self.assertAlmostEqual(r['meanIntervalScore'],160/3)
        self.assertEqual(r['missedGameIds'],['a'])
    def test_empty_and_invalid_evidence(self):
        self.assertIsNone(summarize([],'x','y')['coverage'])
        for bounds in [[1,0],[0,float('inf')],[False,1],[0]]:
            with self.assertRaises(ValueError):summarize([{'id':'a','x':bounds,'y':1}],'x','y')
        r={'id':'a','x':[0,1],'y':0}
        with self.assertRaises(ValueError):summarize([r,r],'x','y')
