"""Reviewed 2026 Highmark entrance reconciliation; not postal geocoding."""
import gzip
import hashlib
import json
import math
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, parse_qs

SOURCES = Path(__file__).resolve().parents[1] / 'data/weather-location-sources'

def require(value, message):
    if not value: raise ValueError(message)

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.hrefs = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a': self.hrefs.extend(value for key, value in attrs if key == 'href' and value)

def validate_candidate(c, sources):
    require(c['officialUrl'] == 'https://www.buffalobills.com/stadium/' and
            c['officialMapUrl'] == 'https://map.concept3d.com/?id=2167', 'Unreviewed official map')
    for key, raw in sources.items():
        require(hashlib.sha256(raw).hexdigest() == c[key], 'Source fingerprint mismatch')
    require(set(sources) == {'officialHtmlHash', 'locationsHash', 'osmResponseHash', 'pointHash'}, 'Incomplete source chain')
    links = Links(); links.feed(sources['officialHtmlHash'].decode('utf-8'))
    require(any(urlparse(h).scheme == 'https' and urlparse(h).netloc == 'map.concept3d.com'
                and parse_qs(urlparse(h).query).get('id') == ['2167'] for h in links.hrefs), 'Official map link missing')
    endpoint = urlparse(c['locationsUrl'])
    require(endpoint.scheme == 'https' and endpoint.netloc == 'api.concept3d.com'
            and endpoint.path.startswith('/categories/') and parse_qs(endpoint.query).get('map') == ['2167'], 'Wrong entrance source')
    categories = json.loads(sources['locationsHash'])
    category = [r for r in categories if r.get('catId') == 107420 and r.get('mapId') == 2167 and r.get('name') == 'Entry 1']
    require(len(category) == 1, 'Ambiguous entrance category')
    entries = [r for r in category[0]['children']['locations'] if r.get('id') == 1203446
               and r.get('catId') == 107420 and r.get('mapId') == 2167 and r.get('name') == 'Entry 1']
    require(len(entries) == 1, 'Named entrance missing or ambiguous')
    entry = entries[0]
    elements = [e for e in json.loads(sources['osmResponseHash'])['elements'] if e.get('type') == 'way' and e.get('id') == 1339149058]
    require(len(elements) == 1 and elements[0] == c['osmElement'], 'Wrong stadium geometry')
    element = elements[0]; tags = element['tags']; bounds = element['bounds']
    require(tags.get('name') == 'Highmark Stadium' and tags.get('leisure') == 'stadium'
            and tags.get('sport') == 'american_football' and tags.get('start_date') == '2026', 'Wrong stadium identity or era')
    for axis, field, point_key, limit in [('lat', 'latitude', 'lat', 90), ('lon', 'longitude', 'lng', 180)]:
        lo, hi, point, midpoint = bounds['min'+axis], bounds['max'+axis], entry[point_key], c[field]
        require(all(type(v) in (int, float) and math.isfinite(v) for v in (lo, hi, point, midpoint)), 'Nonfinite coordinate')
        require(-limit <= lo < hi <= limit and hi-lo < .01 and lo < point < hi and midpoint == (lo+hi)/2, 'Entrance containment or midpoint mismatch')
    require(c['pointUrl'] == f"https://api.weather.gov/points/{c['latitude']:.4f},{c['longitude']:.4f}", 'Wrong NWS request point')
    response = json.loads(sources['pointHash'])
    require(response['geometry']['type'] == 'Point' and response['geometry']['coordinates'] == [round(c['longitude'], 4), round(c['latitude'], 4)], 'Wrong NWS response point')
    require(c['pointState'] == response['properties']['relativeLocation']['properties']['state'] == 'NY', 'Wrong NWS state')
    forecast = urlparse(c['forecastHourly'])
    require(c['forecastHourly'] == response['properties']['forecastHourly'] and forecast.scheme == 'https'
            and forecast.netloc == 'api.weather.gov' and forecast.path.startswith('/gridpoints/BUF/'), 'Wrong NWS forecast grid')
    require(c['validFromSeason'] == 2026 and c['addressStatus'] == 'unresolved-house-number', 'Missing season or address limitation')

def validate_registered_venue(venue):
    c = venue['officialMapEvidence']
    raw = {}
    for key in ('officialHtmlHash', 'locationsHash', 'osmResponseHash', 'pointHash'):
        digest = c[key]
        require(isinstance(digest, str) and len(digest) == 64 and all(ch in '0123456789abcdef' for ch in digest), 'Invalid source identity')
        raw[key] = gzip.decompress((SOURCES / (digest + ('.html.gz' if key == 'officialHtmlHash' else '.json.gz'))).read_bytes())
    validate_candidate(c, raw)
    require(all(venue.get(key) == c[key] for key in ('latitude', 'longitude', 'validFromSeason', 'addressStatus', 'forecastHourly')), 'Registered venue differs from evidence')
    binding = {'mapDataHash': 'osmResponseHash', 'mapElement': 'osmElement', 'pointHash': 'pointHash', 'pointState': 'pointState', 'pointUrl': 'pointUrl'}
    require(all(venue.get(key) == c[value] for key, value in binding.items()), 'Registered source binding differs')
    require(venue.get('mapSource') == 'https://www.openstreetmap.org/way/1339149058'
            and venue.get('attribution') == 'OpenStreetMap contributors' and venue.get('license') == 'ODbL-1.0', 'Missing map attribution')
