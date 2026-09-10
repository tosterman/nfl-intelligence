import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from analytics_report import summarize

class AnalyticsReportTests(unittest.TestCase):
    def test_unavailable_is_not_zero_and_shares_use_pageviews(self):
        r=summarize({'all':{'status':'ok','data':{'pageviews':100,'visitors':20}},
          'games':{'status':'ok','data':{'pageviews':40,'visitors':15}},
          'record':{'status':'unavailable'},'events':{'status':'plan-restricted'}})
        self.assertEqual(r['gamePageviewShare'],0.4)
        self.assertIsNone(r['recordPageviewShare'])
        self.assertEqual(r['metrics']['events']['status'],'plan-restricted')
    def test_zero_denominator_and_invalid_counts_never_become_conversion_claims(self):
        self.assertIsNone(summarize({'all':{'status':'ok','data':{'pageviews':0,'visitors':0}}})['gamePageviewShare'])
        for bad in [-1,True,3.5,'100']:
            with self.assertRaises(ValueError):
                summarize({'all':{'status':'ok','data':{'pageviews':bad,'visitors':0}}})

if __name__=='__main__': unittest.main()
