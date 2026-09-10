import copy,hashlib,json,subprocess,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_data as base

class ReportingTests(unittest.TestCase):
    def test_total_market_uses_its_own_coverage(self):
        records=copy.deepcopy(json.loads((base.ROOT/'data/site.json').read_text())['performance']['records'][:2])
        records[0].update(actualMargin=3,actualTotal=40,marketMargin=None,marketTotal=44)
        records[1].update(actualMargin=7,actualTotal=50,marketMargin=3,marketTotal=None)
        report=base.metrics(records)
        self.assertEqual(report['marketGames'],1);self.assertEqual(report['marketTotalGames'],1)
        self.assertEqual(report['marketTotalMae'],4)
        self.assertEqual(report['matchedModelTotalMae'],round(abs(records[0]['total']-40),3))
        self.assertEqual(report['matchedModelMarginMae'],round(abs(records[1]['homeMargin']-7),3))
        records[0]['marketTotal']=None
        self.assertIsNone(base.metrics(records)['marketTotalMae'])
        self.assertIsNone(base.metrics(records)['matchedModelTotalMae'])
    def test_obsolete_publisher_refuses_without_changing_artifacts(self):
        paths=[base.ROOT/'data/site.json',base.ROOT/'data/ledger.json']
        before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
        result=subprocess.run([sys.executable,str(base.ROOT/'scripts/build_data.py')],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('refresh.py',result.stderr)
        self.assertEqual(before,[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
    def test_regular_and_postseason_partition_accounts_for_every_game(self):
        performance=json.loads((base.ROOT/'data/site.json').read_text())['performance']
        self.assertEqual(sum(group['games'] for group in performance['byPhase']),performance['aggregate']['games'])
        self.assertEqual(sum(group['wins'] for group in performance['byPhase']),performance['aggregate']['wins'])
        self.assertEqual({p['gameType'] for p in performance['records']},{'REG','WC','DIV','CON','SB'})

if __name__=='__main__':unittest.main()
