"""Read-only production probes. No odds acquisition or analytics events are sent."""
import json,re,time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://nfl-intelligence-one.vercel.app'
ENDPOINTS={'forecasts':'/api/status','odds':'/api/odds-status','personnel':'/api/personnel-status','weather':'/api/weather-status','quarterbacks':'/api/quarterback-status','matchup':'/api/matchup-status'}
NFL_TEAMS=set('ARI ATL BAL BUF CAR CHI CIN CLE DAL DEN DET GB HOU IND JAX KC LA LAC LV MIA MIN NE NO NYG NYJ PHI PIT SEA SF TB TEN WAS'.split())

def age(value,now):
    if not isinstance(value,str):raise ValueError('Missing acquisition timestamp')
    try:at=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError:raise ValueError('Invalid acquisition timestamp') from None
    if at.tzinfo is None:raise ValueError('Timestamp lacks timezone')
    return (now-at).total_seconds()/3600

def validate_health(kind,http_status,payload,now):
    if http_status!=200 or not isinstance(payload,dict) or payload.get('status')!='ok':
        raise ValueError('Endpoint did not report healthy HTTP 200')
    if kind=='odds':
        if payload.get('maximumAgeHours')!=6 or not 0<=age(payload.get('fetchedAt'),now)<=6:
            raise ValueError('Odds acquisition is missing, stale or future-dated')
    elif kind=='matchup':
        if payload.get('maximumAgeHours')!=30 or type(payload.get('season')) is not int or payload['season']!=payload.get('expectedSeason') or not now.year-1<=payload['season']<=now.year:
            raise ValueError('Matchup season or age policy invalid')
        if type(payload.get('week')) is not int or not 1<=payload['week']<=22 or payload['week']!=payload.get('expectedWeek'):
            raise ValueError('Matchup week mismatch')
        if payload.get('gameType') not in ('REG','POST') or payload['gameType']!=payload.get('expectedGameType'):
            raise ValueError('Matchup season phase mismatch')
        observed=age(payload.get('sourceObservedAt'),now)
        cutoff=payload.get('cutoff')
        if not isinstance(cutoff,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',cutoff) or age(cutoff+'T00:00:00+00:00',now)<observed:
            raise ValueError('Matchup cutoff is invalid or postdates observation')
        if not 0<=observed<=age(payload.get('checkedAt'),now)<30 or not observed-30<=age(payload.get('expiresAt'),now)<0:
            raise ValueError('Matchup source is stale or future-dated')
        if any(not re.fullmatch(r'[a-f0-9]{64}',payload.get(k,'')) for k in ['sourceHash','scheduleHash']):
            raise ValueError('Matchup source identities missing')
        count=payload.get('gameCount');state=payload.get('sampleStatus')
        if type(count) is not int or not ((state=='no-eligible-games' and count==0) or (state=='available' and count>0)):
            raise ValueError('Matchup sample state and count disagree')
    elif kind=='personnel':
        if payload.get('maximumAgeHours')!=30 or payload.get('collectionStatus')!='ok':
            raise ValueError('Personnel collection failed')
        season=payload.get('season')
        if type(season) is not int or not now.year-1<=season<=now.year or season!=payload.get('expectedSeason'):
            raise ValueError('Personnel season mismatch')
        if any(not 0<=age(payload.get(k),now)<30 for k in ['checkedAt','retrievedAt','assetUpdatedAt']):
            raise ValueError('Personnel acquisition or source is stale')
        if age(payload['assetUpdatedAt'],now)<age(payload['retrievedAt'],now):
            raise ValueError('Personnel source postdates acquisition')
        if type(payload.get('rowCount')) is not int or payload['rowCount']<=0 or not re.fullmatch(r'[a-f0-9]{64}',payload.get('sourceHash','')):
            raise ValueError('Personnel source identity missing')
    elif kind=='quarterbacks':
        if payload.get('maximumAgeHours')!=30 or payload.get('collectionStatus')!='ok':raise ValueError('Quarterback collection failed')
        season=payload.get('season')
        if type(season) is not int or not now.year-1<=season<=now.year or season!=payload.get('expectedSeason'):raise ValueError('Quarterback season mismatch')
        if any(not 0<=age(payload.get(k),now)<30 for k in ['checkedAt','retrievedAt','assetUpdatedAt']):raise ValueError('Quarterback source is stale')
        if not re.fullmatch(r'[a-f0-9]{64}',payload.get('sourceHash','')):raise ValueError('Quarterback source identity missing')
        expected=payload.get('expectedTeams');checks=payload.get('checks')
        if not isinstance(expected,list) or len(expected)!=32 or any(not isinstance(t,str) for t in expected) or set(expected)!=NFL_TEAMS:raise ValueError('Expected quarterback team set incomplete')
        if not isinstance(checks,list) or len(checks)!=32 or any(not isinstance(c,dict) or not isinstance(c.get('team'),str) or c.get('status')!='ok' or not 0<=age(c.get('recordedAt'),now)<30 for c in checks):raise ValueError('Quarterback role checks incomplete or stale')
        if {c['team'] for c in checks}!=NFL_TEAMS:raise ValueError('Quarterback team checks mismatch')
        if age(payload['assetUpdatedAt'],now)<age(payload['retrievedAt'],now) or any(age(c['recordedAt'],now)<age(payload['retrievedAt'],now) for c in checks):raise ValueError('Quarterback source postdates acquisition')
    elif kind=='weather':
        if payload.get('maximumAgeHours')!=30 or not 0<=age(payload.get('generatedAt'),now)<30:
            raise ValueError('Weather collection is stale')
        if not age(payload['generatedAt'],now)<=age(payload.get('collectionStartedAt'),now)<30:
            raise ValueError('Weather collection start is invalid or stale')
        checks=payload.get('checks');count=payload.get('eligibleGames')
        if type(count) is not int or count<0 or not isinstance(checks,list) or len(checks)!=count or type(payload.get('availableGames')) is not int or payload['availableGames']!=count:
            raise ValueError('Weather coverage counts are inconsistent')
        if any(not isinstance(c,dict) or c.get('status')!='ok' or not isinstance(c.get('gameId'),str) or not c['gameId'] for c in checks):
            raise ValueError('Weather game checks are incomplete')
        if len({c['gameId'] for c in checks})!=count:raise ValueError('Duplicate weather game checks')
        for check in checks:
            if any(not -5/60<=age(check.get(k),now)<=30 for k in ['issuedAt','retrievedAt']) or not re.fullmatch(r'[a-f0-9]{64}',check.get('sourceHash','')):
                raise ValueError('Weather source is stale or unidentified')
    elif kind=='forecasts':
        checks=payload.get('checks')
        if not isinstance(checks,list) or len(checks)!=4 or any(not isinstance(c,dict) for c in checks):
            raise ValueError('Forecast health checks are incomplete')
        names=[c.get('name') for c in checks]
        if any(not isinstance(n,str) for n in names) or len(set(names))!=4 or not {'Model edition','Schedule and results'}.issubset(names):
            raise ValueError('Forecast health identities are invalid')
        years=sorted(int(n[:4]) for n in names if re.fullmatch(r'\d{4} efficiency source',n))
        season=payload.get('season')
        if type(season) is not int or not now.year-1<=season<=now.year or years!=[season-1,season]:
            raise ValueError('Recent efficiency sources are missing')
        if any(c.get('status')!='ok' or not -5/60<=age(c.get('retrievedAt'),now)<=30 for c in checks):
            raise ValueError('A forecast input is invalid or older than thirty hours')
        edition=next(c['retrievedAt'] for c in checks if c['name']=='Model edition')
        if age(payload.get('generatedAt'),now)!=age(edition,now) or not isinstance(payload.get('modelVersion'),str) or not payload['modelVersion'] or not re.fullmatch(r'[a-f0-9]{64}',payload.get('sourceHash','')):
            raise ValueError('Forecast identity is incomplete or inconsistent')
    else:raise ValueError('Unknown probe')

def health_evidence(kind, payload):
    keys = {
        'forecasts': ('generatedAt','modelVersion','sourceHash'),
        'odds': ('fetchedAt','maximumAgeHours'),
        'personnel': ('retrievedAt','assetUpdatedAt','sourceHash','rowCount','collectionStatus'),
        'quarterbacks': ('retrievedAt','assetUpdatedAt','sourceHash','collectionStatus'),
        'weather': ('collectionStartedAt','generatedAt','eligibleGames','availableGames'),
        'matchup': ('season','week','gameType','cutoff','sourceObservedAt','expiresAt','sourceHash','scheduleHash','sampleStatus','gameCount'),
    }[kind]
    return {key:payload[key] for key in keys}


def edition_parity(expected, observed):
    try:
        intended = {'generatedAt':expected['generatedAt'], 'modelVersion':expected['modelVersion'], 'sourceHash':expected['source']['sha256']}
        if not isinstance(observed,dict) or any(key not in observed for key in intended):
            raise ValueError('Missing published identity')
        if not all(isinstance(value,str) and value for value in intended.values()):
            raise ValueError('Invalid intended identity')
        if not re.fullmatch(r'[a-f0-9]{64}',intended['sourceHash']):raise ValueError('Invalid source identity')
        checked=datetime.now(timezone.utc)
        expected_age=age(intended['generatedAt'],checked)
        observed_age=age(observed['generatedAt'],checked)
        # Compare instants directly: equivalent timezone spellings are one edition.
        same_time=datetime.fromisoformat(intended['generatedAt'].replace('Z','+00:00')) == datetime.fromisoformat(observed['generatedAt'].replace('Z','+00:00'))
        matches=same_time and all(intended[k]==observed[k] for k in ['modelVersion','sourceHash'])
        status='matching' if matches else 'behind-intended' if observed_age > expected_age and not same_time else 'different-identity'
        return {'status':status,'intended':intended,'observed':{k:observed[k] for k in intended}}
    except (KeyError,TypeError,ValueError):
        return {'status':'unverified'}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None

def probe(kind):
    attempts=[]
    for attempt in range(2):
        result={'observedAt':datetime.now(timezone.utc).isoformat(),'httpStatus':None,'healthy':False}
        try:
            request=Request(ORIGIN+ENDPOINTS[kind],headers={'User-Agent':'NFL-Intelligence-Health/1.0','Cache-Control':'no-cache'})
            with build_opener(NoRedirect()).open(request,timeout=10) as response:
                result['httpStatus']=response.status
                raw=response.read(100001)
                if len(raw)>100000:raise ValueError('Health response exceeded limit')
                payload=json.loads(raw)
                validate_health(kind,response.status,payload,datetime.now(timezone.utc))
                result.update(healthy=True,reason='Verified status and acquisition times',evidence=health_evidence(kind,payload))
        except HTTPError as error:
            result.update(httpStatus=error.code,reason='Unhealthy HTTP response or redirect')
        except (URLError,TimeoutError,OSError):result['reason']='Network request failed'
        except (ValueError,TypeError,KeyError):result['reason']='Invalid, incomplete or stale health payload'
        attempts.append(result)
        if result['healthy']:break
        if attempt==0:time.sleep(2)
    return {'endpoint':ENDPOINTS[kind],'healthy':attempts[-1]['healthy'],'attempts':attempts}

def main():
    with ThreadPoolExecutor(max_workers=3) as executor:
        results=dict(zip(ENDPOINTS,executor.map(probe,ENDPOINTS)))
    try:
        expected=json.loads((ROOT/'data/site.json').read_text())
    except (OSError,ValueError):expected={}
    parity=edition_parity(expected,results['forecasts']['attempts'][-1].get('evidence'))
    feeds_healthy=all(r['healthy'] for r in results.values())
    report={'checkedAt':datetime.now(timezone.utc).isoformat(),'healthy':feeds_healthy and parity['status']=='matching',
            'feedsHealthy':feeds_healthy,'editionParity':parity,'checks':results}
    output=ROOT/'release-recovery'/'health-report.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 0 if report['healthy'] else 1

if __name__=='__main__':raise SystemExit(main())
