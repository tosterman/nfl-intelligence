"""Conservative consistency check for recorded Census address evidence."""
import math,re

ABBREVIATIONS={'STREET':'ST','AVENUE':'AVE','DRIVE':'DR','PLACE':'PL','CIRCLE':'CIR',
 'HIGHWAY':'HWY','ROAD':'RD','NORTH':'N','SOUTH':'S','EAST':'E','WEST':'W'}

def words(value):
    return [ABBREVIATIONS.get(w,w) for w in re.findall(r'[A-Z0-9]+',value.upper())]

def validate_venue(venue):
    if venue.get('status')!='confirmed-address-geocode':return
    matches=venue.get('geocodeMatches',[])
    if len(matches)!=1:raise ValueError('Venue requires one recorded Census match')
    match=matches[0]
    requested=venue['address'].split(',');returned=match['matchedAddress'].split(',')
    # Compare street, municipality, and state. Postal boundaries can differ for
    # an interpolated vicinity point, so ZIP equality is not asserted here.
    if len(requested)!=3 or len(returned)!=4 or words(requested[0])!=words(returned[0]) or words(requested[1])!=words(returned[1]) or words(requested[2])[:1]!=words(returned[2]):
        raise ValueError('Returned Census address does not match official street and locality')
    coords=match['coordinates']
    for name,key,limit in [('latitude','y',90),('longitude','x',180)]:
        value=venue.get(name)
        if type(value) not in (int,float) or not math.isfinite(value) or abs(value)>limit or value!=coords.get(key):
            raise ValueError('Venue coordinates differ from recorded Census match')
