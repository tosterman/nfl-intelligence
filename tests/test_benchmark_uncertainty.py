import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from benchmark_uncertainty import compare
class BenchmarkTests(unittest.TestCase):
    def row(self,id,week,model=3,market=1,season=2025):return dict(id=id,week=week,season=season,model=model,market=market,actual=0)
    def run_compare(self,rows):return compare(rows,'model','market','actual',draws=1000)
    def test_constant_paired_difference_and_week_clusters(self):
        rows=[self.row('a',1),self.row('b',1),self.row('c',2),self.row('d',2,season=2024),self.row('e',3,season=2024)]
        r=self.run_compare(rows)
        self.assertEqual(r['difference'],2);self.assertEqual(r['interval95'],[2,2]);self.assertEqual(r['clustersBySeason'],{'2024':2,'2025':2})
    def test_same_game_matching_and_sparse_samples(self):
        r=self.run_compare([self.row('a',1,model=9,market=None),self.row('b',2)])
        self.assertEqual(r['modelMae'],3);self.assertEqual(r['games'],1);self.assertEqual(r['excludedGames'],1);self.assertIsNone(r['interval95'])
        self.assertIsNone(self.run_compare([])['difference'])
    def test_duplicate_invalid_values_fail_and_seed_is_reproducible(self):
        for rows in [[self.row('a',1),self.row('a',2)],[self.row('a',1,model=float('nan'))]]:
            with self.assertRaises(ValueError):self.run_compare(rows)
        rows=[self.row('a',1,model=0),self.row('b',1,model=8),self.row('c',2,model=2)]
        self.assertEqual(self.run_compare(rows),self.run_compare(rows[::-1]))
        r=self.run_compare(rows)
        self.assertAlmostEqual(r['difference'],7/3)
        self.assertEqual(r['interval95'],[1,3])
if __name__=='__main__':unittest.main()
