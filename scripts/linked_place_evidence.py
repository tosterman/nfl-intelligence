"""Check the reviewed Acrisure candidate; does not authorize new venue links.

The HTML extraction remains a reviewed observation. Source digests are identifiers,
not proof that a website attested to these fields. Raw OSM/NWS bytes are verified.
"""
import hashlib
import json
import math
import gzip
from pathlib import Path
from venue_evidence import words

OFFICIAL = 'https://acrisurestadium.com/event/pittsburgh-steelers-vs-atlanta-falcons-2/'
PLACE = 'https://www.waze.com/live-map/directions/acrisure-stadium-art-rooney-ave-100-pittsburgh?to=place.w.183501204.1834880973.255564'


def validate_registered_venue(venue):
    c = venue['linkedPlaceEvidence']
    sources = Path(__file__).resolve().parents[1] / 'data/weather-location-sources'
    raw = []
    for key in ('osmResponseHash', 'pointHash'):
        digest = c[key]
        require(isinstance(digest, str) and len(digest) == 64
                and all(ch in '0123456789abcdef' for ch in digest), 'Invalid source digest')
        raw.append(gzip.decompress((sources / (digest + '.json.gz')).read_bytes()))
    validate_candidate(c, *raw)
    binding = {'latitude': 'derivedLatitude', 'longitude': 'derivedLongitude',
               'mapElement': 'osmElement', 'mapDataHash': 'osmResponseHash',
               'pointHash': 'pointHash', 'pointUrl': 'pointUrl', 'pointState': 'pointState',
               'forecastHourly': 'forecastHourly', 'addressSource': 'officialLinkSource'}
    require(all(venue.get(key) == c[value] for key, value in binding.items()),
            'Registered venue differs from reviewed evidence')
    require(venue.get('address') == '100 Art Rooney Avenue, Pittsburgh, PA 15212'
            and venue.get('mapSource') == 'https://www.openstreetmap.org/way/24722790',
            'Registered address or map source mismatch')
    require(venue.get('license') == 'ODbL-1.0'
            and venue.get('attribution') == 'OpenStreetMap contributors', 'Map attribution missing')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_candidate(candidate, osm_raw, point_raw):
    """Validate factual consistency of a candidate against retained map responses."""
    c = candidate
    require(c.get('officialLinkSource') == OFFICIAL and c.get('linkedPlaceUrl') == PLACE
            and c.get('officialLinkPresent') is True, 'Unreviewed official place reference')
    for key in ('officialHtmlHash', 'linkedPlaceHtmlHash'):
        value = c.get(key)
        require(isinstance(value, str) and len(value) == 64
                and all(ch in '0123456789abcdef' for ch in value), 'Missing HTML source digest')
    place = c['place']
    address = place['address']
    require(place.get('name') == 'Acrisure Stadium'
            and words(address.get('streetAddress', '')) == words('100 Art Rooney Avenue')
            and words(address.get('addressLocality', '')) == ['PITTSBURGH']
            and address.get('addressRegion') == 'Pennsylvania'
            and address.get('addressCountry') == 'United States', 'Linked place address mismatch')
    for key, raw in [('osmResponseHash', osm_raw), ('pointHash', point_raw)]:
        require(hashlib.sha256(raw).hexdigest() == c.get(key), 'Retained response digest mismatch')
    elements = json.loads(osm_raw)['elements']
    matches = [e for e in elements if e.get('tags', {}).get('name') == 'Acrisure Stadium'
               and e.get('tags', {}).get('leisure') == 'stadium']
    require(len(matches) == 1 and matches[0] == c['osmElement'], 'Stadium geometry is ambiguous or differs')
    element = matches[0]
    require(element.get('type') == 'way' and element.get('id') == 24722790, 'Unreviewed stadium feature')
    tags = element['tags']
    # This fallback only covers missing address tags. Any future tagged address
    # must be reviewed through the existing address reconciliation path.
    require(not any(key.startswith('addr:') for key in tags), 'Map address tags require separate reconciliation')
    bounds = element['bounds']
    for axis, field, limit in [('lat', 'Latitude', 90), ('lon', 'Longitude', 180)]:
        lo, hi = bounds['min' + axis], bounds['max' + axis]
        point, midpoint = c['place' + field], c['derived' + field]
        require(all(type(v) in (int, float) and math.isfinite(v) for v in (lo, hi, point, midpoint)),
                'Nonfinite stadium coordinates')
        require(-limit <= lo < hi <= limit and hi - lo <= .05
                and lo < point < hi and midpoint == (lo + hi) / 2, 'Stadium containment or midpoint mismatch')
    latitude, longitude = c['derivedLatitude'], c['derivedLongitude']
    require(c.get('pointUrl') == f'https://api.weather.gov/points/{latitude:.4f},{longitude:.4f}',
            'NWS request differs from stadium midpoint')
    response = json.loads(point_raw)
    require(response['geometry']['type'] == 'Point'
            and response['geometry']['coordinates'] == [round(longitude, 4), round(latitude, 4)],
            'NWS response coordinates mismatch')
    properties = response['properties']
    require(c.get('pointState') == 'PA'
            and properties['relativeLocation']['properties']['state'] == 'PA', 'NWS state mismatch')
    require(c.get('forecastHourly') == properties['forecastHourly']
            == 'https://api.weather.gov/gridpoints/PBZ/77,66/forecast/hourly', 'NWS grid mismatch')
