"""Acquire real NWS kickoff-hour context; never changes numerical forecasts."""
import gzip,hashlib,json,math,urllib.request
from datetime import datetime,timezone,timedelta
from pathlib import Path
from urllib.parse import urlparse
from venue_evidence import validate_venue

ROOT=Path(__file__).resolve().parents[1]
USER_AGENT='NFLIntelligence (https://github.com/tosterman/nfl-intelligence)'

def parse_time(value):
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:raise ValueError('Timezone required')
    return result

def read_nws(url):
    parsed=urlparse(url)
    if parsed.scheme!='https' or parsed.netloc!='api.weather.gov':raise ValueError('Unexpected weather source')
    request=urllib.request.Request(url,headers={'User-Agent':USER_AGENT,'Accept':'application/geo+json'})
    payload=urllib.request.urlopen(request,timeout=20).read()
    data=json.loads(payload);digest=hashlib.sha256(payload).hexdigest()
    folder=ROOT/'data/weather-sources';folder.mkdir(parents=True,exist_ok=True)
    (folder/(digest+'.json.gz')).write_bytes(gzip.compress(payload,mtime=0))
    return data,digest

def kickoff_period(payload,kickoff,retrieved):
    properties=payload['properties'];issued=parse_time(properties['updateTime'])
    if issued>retrieved+timedelta(minutes=5) or retrieved-issued>timedelta(hours=30):raise ValueError('Stale or future forecast issue time')
    period=next((p for p in properties['periods'] if parse_time(p['startTime'])<=kickoff<parse_time(p['endTime'])),None)
    if period is None:raise ValueError('Kickoff outside available forecast horizon')
    temperature=period.get('temperature')
    if temperature is not None and (isinstance(temperature,bool) or not isinstance(temperature,(int,float)) or not math.isfinite(temperature)):raise ValueError('Invalid temperature')
    if period.get('temperatureUnit') not in ['F','C']:raise ValueError('Unsupported temperature unit')
    rain=(period.get('probabilityOfPrecipitation') or {}).get('value')
    if rain is not None and (isinstance(rain,bool) or not isinstance(rain,(int,float)) or not math.isfinite(rain) or not 0<=rain<=100):raise ValueError('Invalid precipitation probability')
    return {'issuedAt':issued.isoformat(),'periodStart':period['startTime'],'periodEnd':period['endTime'],'temperature':temperature,'temperatureUnit':period['temperatureUnit'],'precipitationProbability':rain,'windSpeed':period.get('windSpeed'),'windDirection':period.get('windDirection'),'summary':period.get('shortForecast')}

def acquire_game(game,venues,now,fetch=read_nws):
    result={'status':'unavailable','gameId':game['id'],'kickoff':game['kickoff'],'venue':game['venue']}
    if not game.get('kickoff'):return result|{'reason':'Kickoff time unavailable'}
    kickoff=parse_time(game['kickoff'])
    if kickoff<=now:return result|{'reason':'Pregame forecast collection has closed'}
    if kickoff-now>timedelta(days=7):return result|{'reason':'Outside the seven-day collection window'}
    venue=venues.get(game['venue'],{})
    coords=[venue.get('latitude'),venue.get('longitude')]
    if game.get('neutral') or not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in coords):return result|{'reason':'Verified US venue location unavailable'}
    lat,lon=coords
    if not -90<=lat<=90 or not -180<=lon<=180:raise ValueError('Invalid venue coordinates')
    point_url=f'https://api.weather.gov/points/{lat:.4f},{lon:.4f}'
    points,point_hash=fetch(point_url)
    forecast_url=points['properties']['forecastHourly']
    forecast,source_hash=fetch(forecast_url)
    retrieved=datetime.now(timezone.utc)
    if retrieved>=kickoff:return result|{'reason':'Kickoff passed during acquisition'}
    values=kickoff_period(forecast,kickoff,retrieved)
    return result|values|{'status':'available','retrievedAt':retrieved.isoformat(),'sourceUrl':forecast_url,'sourceHash':source_hash,'pointUrl':point_url,'pointHash':point_hash,'latitude':lat,'longitude':lon,'locationEvidence':venue,'modelAdjustment':False}

def main():
    site=json.loads((ROOT/'data/site.json').read_text());venues=json.loads((ROOT/'data/weather-venues.json').read_text())
    osm=json.loads((ROOT/'data/weather-osm-venues.json').read_text())
    if any(venues[name].get('status')!='unavailable' for name in set(venues)&set(osm)):raise ValueError('Conflicting venue evidence sources')
    venues.update(osm)
    for venue in venues.values():validate_venue(venue)
    now=datetime.now(timezone.utc);games={};path=ROOT/'data/weather-ledger.json'
    ledger=json.loads(path.read_text()) if path.exists() else []
    hashes={s['hash'] for s in ledger}
    for game in site['games']:
        try:record=acquire_game(game,venues,now)
        except Exception as error:
            record={'status':'unavailable','gameId':game['id'],'kickoff':game['kickoff'],'venue':game['venue'],'reason':'Forecast temporarily unavailable'}
            print(f'{game["id"]}: {type(error).__name__}: {error}')
        games[game['id']]=record
        if record['status']=='available':
            digest=hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            if digest not in hashes:ledger.append(record|{'hash':digest});hashes.add(digest)
    path.write_text(json.dumps(ledger,indent=2)+'\n')
    (ROOT/'data/weather.json').write_text(json.dumps({'collectionStartedAt':now.isoformat(),'generatedAt':datetime.now(timezone.utc).isoformat(),'games':games},indent=2)+'\n')
    print(f'Weather context: {sum(g["status"]=="available" for g in games.values())} games. Numerical forecasts unchanged.')

if __name__=='__main__':main()
