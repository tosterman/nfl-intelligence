import sys,unittest,json,tempfile,threading,io
from contextlib import redirect_stdout
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from production_health import validate_health
import production_health

class ProductionHealthTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,9,10,18,tzinfo=timezone.utc)
        self.at=self.now.isoformat()
        self.forecast={'status':'ok','season':2026,'generatedAt':self.at,'sourceHash':'a'*64,'modelVersion':'v1',
            'checks':[{'name':n,'retrievedAt':self.at,'status':'ok'} for n in ['Model edition','Schedule and results','2025 efficiency source','2026 efficiency source']]}
    def test_actual_timestamps_override_rounded_or_claimed_health(self):
        validate_health('forecasts',200,self.forecast,self.now)
        self.forecast['checks'][1]['retrievedAt']=(self.now-timedelta(hours=30,seconds=1)).isoformat()
        with self.assertRaises(ValueError):validate_health('forecasts',200,self.forecast,self.now)
    def test_missing_checks_false_green_and_unhealthy_http_fail(self):
        for status,payload in [(503,self.forecast),(200,{'status':'ok'}),(200,{**self.forecast,'checks':[]})]:
            with self.assertRaises(ValueError):validate_health('forecasts',status,payload,self.now)
        self.forecast['checks'][2]['name']='2098 efficiency source'
        self.forecast['checks'][3]['name']='2099 efficiency source'
        with self.assertRaises(ValueError):validate_health('forecasts',200,self.forecast,self.now)
    def test_odds_stale_future_and_missing_acquisition_fail(self):
        good={'status':'ok','fetchedAt':self.at,'maximumAgeHours':6}
        validate_health('odds',200,good,self.now)
        for at in [None,(self.now+timedelta(seconds=1)).isoformat(),(self.now-timedelta(hours=6,seconds=1)).isoformat()]:
            with self.assertRaises(ValueError):validate_health('odds',200,{**good,'fetchedAt':at},self.now)

    def test_http_failure_drill_returns_nonzero_and_retains_both_attempts(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                failed=self.path=='/api/status'
                self.send_response(503 if failed else 200)
                self.send_header('Content-Type','application/json');self.end_headers()
                at=datetime.now(timezone.utc).isoformat()
                payload={'status':'ok','fetchedAt':at,'maximumAgeHours':6}
                if self.path=='/api/personnel-status':payload={'status':'ok','collectionStatus':'ok','season':datetime.now(timezone.utc).year,'expectedSeason':datetime.now(timezone.utc).year,'checkedAt':at,'retrievedAt':at,'assetUpdatedAt':at,'sourceHash':'a'*64,'rowCount':1,'maximumAgeHours':30}
                if self.path=='/api/weather-status':payload={'status':'ok','collectionStartedAt':at,'generatedAt':at,'maximumAgeHours':30,'eligibleGames':0,'availableGames':0,'checks':[]}
                self.wfile.write(json.dumps(payload).encode())
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            with tempfile.TemporaryDirectory() as folder,patch.object(production_health,'ROOT',Path(folder)),patch.object(production_health,'ORIGIN',f'http://127.0.0.1:{server.server_port}'),redirect_stdout(io.StringIO()):
                self.assertEqual(production_health.main(),1)
                report=json.loads((Path(folder)/'release-recovery/health-report.json').read_text())
                self.assertFalse(report['healthy'])
                self.assertEqual([a['httpStatus'] for a in report['checks']['forecasts']['attempts']],[503,503])
                self.assertTrue(report['checks']['odds']['healthy'])
                self.assertTrue(report['checks']['personnel']['healthy'])
                self.assertTrue(report['checks']['weather']['healthy'])
        finally:server.shutdown();server.server_close();worker.join()

    def test_personnel_failure_and_old_asset_override_claimed_health(self):
        good={'status':'ok','collectionStatus':'ok','season':2026,'expectedSeason':2026,'checkedAt':self.at,'retrievedAt':self.at,'assetUpdatedAt':self.at,'sourceHash':'a'*64,'rowCount':1,'maximumAgeHours':30}
        validate_health('personnel',200,good,self.now)
        for change in [{'collectionStatus':'unavailable'},{'season':2025},{'rowCount':0},{'assetUpdatedAt':(self.now-timedelta(hours=30)).isoformat()},{'checkedAt':(self.now+timedelta(seconds=1)).isoformat()}]:
            with self.assertRaises(ValueError):validate_health('personnel',200,good|change,self.now)

    def test_weather_checks_counts_and_source_ages(self):
        good={'status':'ok','collectionStartedAt':self.at,'generatedAt':self.at,'maximumAgeHours':30,'eligibleGames':1,'availableGames':1,
            'checks':[{'gameId':'g','status':'ok','issuedAt':self.at,'retrievedAt':self.at,'sourceHash':'a'*64}]}
        validate_health('weather',200,good,self.now)
        for change in [{'eligibleGames':0},{'checks':[]},{'availableGames':0},
            {'checks':[{**good['checks'][0],'issuedAt':(self.now-timedelta(hours=31)).isoformat()}]},
            {'generatedAt':(self.now+timedelta(seconds=1)).isoformat()}]:
            with self.assertRaises(ValueError):validate_health('weather',200,good|change,self.now)

if __name__=='__main__':unittest.main()
