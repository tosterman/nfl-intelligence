import gzip,hashlib,json,sys,unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import refresh_weather as weather

class WeatherTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,9,10,12,tzinfo=timezone.utc)
        self.payload={'properties':{'updateTime':self.now.isoformat(),'periods':[{'startTime':'2026-09-10T13:00:00+00:00','endTime':'2026-09-10T14:00:00+00:00','temperature':None,'temperatureUnit':'F','probabilityOfPrecipitation':{'value':None},'windSpeed':'5 mph'}]}}
    def test_period_contains_kickoff_and_missing_values_stay_missing(self):
        p=weather.kickoff_period(self.payload,self.now+timedelta(hours=1,minutes=35),self.now)
        self.assertIsNone(p['temperature']);self.assertIsNone(p['precipitationProbability'])
    def test_exact_period_end_does_not_use_previous_hour(self):
        with self.assertRaisesRegex(ValueError,'horizon'):weather.kickoff_period(self.payload,self.now+timedelta(hours=2),self.now)
    def test_stale_issue_and_invalid_rain_fail_closed(self):
        self.payload['properties']['updateTime']=(self.now-timedelta(hours=31)).isoformat()
        with self.assertRaises(ValueError):weather.kickoff_period(self.payload,self.now+timedelta(hours=1),self.now)
        self.payload['properties']['updateTime']=self.now.isoformat()
        self.payload['properties']['periods'][0]['probabilityOfPrecipitation']['value']=101
        with self.assertRaises(ValueError):weather.kickoff_period(self.payload,self.now+timedelta(hours=1),self.now)
    def test_neutral_game_never_falls_back_to_designated_home_location(self):
        game={'id':'g','kickoff':(self.now+timedelta(days=1)).isoformat(),'venue':'Stadium','neutral':True}
        def forbidden(url):raise AssertionError('No request allowed')
        result=weather.acquire_game(game,{'Stadium':{'latitude':39,'longitude':-75}},self.now,forbidden)
        self.assertEqual(result['status'],'unavailable')
    def test_closed_and_unmapped_games_never_fetch(self):
        def forbidden(url):raise AssertionError('No request allowed')
        for kickoff in [None,(self.now-timedelta(seconds=1)).isoformat(),(self.now+timedelta(days=8)).isoformat(),(self.now+timedelta(days=1)).isoformat()]:
            result=weather.acquire_game({'id':'g','venue':'Unknown','kickoff':kickoff}, {},self.now,forbidden)
            self.assertEqual(result['status'],'unavailable')
    def test_untrusted_link_cannot_be_requested(self):
        with self.assertRaises(ValueError):weather.read_nws('https://example.com/private')
    def test_recorded_forecasts_have_reproducible_source_bytes(self):
        root=Path(__file__).resolve().parents[1]
        ledger=json.loads((root/'data/weather-ledger.json').read_text())
        for record in ledger:
            for key in ['sourceHash','pointHash']:
                payload=gzip.decompress((root/'data/weather-sources'/(record[key]+'.json.gz')).read_bytes())
                self.assertEqual(hashlib.sha256(payload).hexdigest(),record[key])
            forecast=json.loads(gzip.decompress((root/'data/weather-sources'/(record['sourceHash']+'.json.gz')).read_bytes()))
            period=weather.kickoff_period(forecast,weather.parse_time(record['kickoff']),weather.parse_time(record['retrievedAt']))
            self.assertEqual(period['temperature'],record['temperature'])
            self.assertEqual(period['periodStart'],record['periodStart'])

if __name__=='__main__':unittest.main()
