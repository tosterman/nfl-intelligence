# Pittsburgh weather location investigation

The official stadium parking guide and Pitt Athletics facility page agree on 100 Art Rooney Avenue. The stadium's tours/museum contact page uses 900 Art Rooney Avenue. These are distinct source meanings; the alternate contact address is not a correction to the stadium guide.

The retained Census query for 100 has no unique match. A new Census query for 900 also returned no matches. Retained OSM way 24722790 has a named stadium outline but no address tags. A new bounding-box query of nearby address-bearing features did not establish a matching stadium address. Its raw response and the alternate Census response are retained by SHA-256 in `data/weather-location-sources`; `acrisure-location-review.json` records their identities and the query.

Coordinates remain withheld. This investigation does not expand the current seventeen verified US locations. Accepting this stadium requires a primary geospatial reference or an independently reconciled location record, rather than relaxing the existing address check or borrowing a nearby facility's address. Weather forecasts remain descriptive context, with no numerical adjustment to the model.
