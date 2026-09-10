"""Acquire reviewable OSM venue candidates; never updates the production venue map."""
import gzip,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from venue_evidence import validate_venue

ROOT=Path(__file__).resolve().parents[1]
AGENT='NFLIntelligence/1.0 (https://github.com/tosterman/nfl-intelligence)'

def fetch(url):
    raw=urlopen(Request(url,headers={'User-Agent':AGENT}),timeout=35).read()
    payload=json.loads(raw)
    if payload.get('remark') or payload.get('error'):raise ValueError('Provider reported incomplete or failed response')
    digest=hashlib.sha256(raw).hexdigest()
    folder=ROOT/'data/weather-location-sources';folder.mkdir(exist_ok=True)
    (folder/(digest+'.json.gz')).write_bytes(gzip.compress(raw,mtime=0))
    return payload,digest

def main(names):
    official=json.loads((ROOT/'data/weather-venues.json').read_text())
    if not names or len(set(names))!=len(names) or any(n not in official for n in names):raise ValueError('Select unique venues with recorded official addresses')
    query='[out:json][timeout:25];('+''.join('nwr["leisure"="stadium"]["name"='+json.dumps(n)+'];' for n in names)+');out tags bb;'
    url='https://overpass-api.de/api/interpreter?'+urlencode({'data':query})
    response,digest=fetch(url);at=datetime.now(timezone.utc).isoformat();candidates={};rejected={}
    for name in names:
        matches=[e for e in response['elements'] if e.get('tags',{}).get('name')==name]
        if len(matches)!=1:rejected[name]='Expected exactly one named stadium object';continue
        e=matches[0];bounds=e.get('bounds')
        if not bounds:rejected[name]='Stadium bounds unavailable';continue
        lat=(bounds['minlat']+bounds['maxlat'])/2;lon=(bounds['minlon']+bounds['maxlon'])/2
        point_url=f'https://api.weather.gov/points/{lat:.4f},{lon:.4f}'
        point,point_hash=fetch(point_url);p=point['properties']
        candidate={k:official[name][k] for k in ['address','addressSource']}
        candidate.update(status='confirmed-osm-stadium',latitude=lat,longitude=lon,
            coordinateMeaning='Midpoint of a named OpenStreetMap stadium bounding box, reconciled to the official address. Area forecast lookup only; not surveyed field coordinates.',
            mapSource=f'https://www.openstreetmap.org/{e["type"]}/{e["id"]}',mapElement=e,mapDataSource=url,mapDataHash=digest,retrievedAt=at,
            attribution='OpenStreetMap contributors',license='ODbL-1.0',licenseUrl='https://www.openstreetmap.org/copyright',
            pointUrl=point_url,pointHash=point_hash,pointCheckedAt=datetime.now(timezone.utc).isoformat(),pointState=p['relativeLocation']['properties']['state'],
            pointCity=p['relativeLocation']['properties']['city'],forecastHourly=p['forecastHourly'])
        try:validate_venue(candidate)
        except (ValueError,KeyError):rejected[name]='Map geometry or address does not reconcile to official evidence';continue
        candidates[name]=candidate
    report={'retrievedAt':at,'mapDataSource':url,'mapDataHash':digest,'candidates':candidates,'rejected':rejected}
    (ROOT/'reviews/venue-map-candidates.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'candidates':list(candidates),'rejected':rejected},indent=2))

if __name__=='__main__':main(sys.argv[1:])
