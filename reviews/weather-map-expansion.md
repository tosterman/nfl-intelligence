# Map-based weather coverage — September 10, 2026

Five additional stadium locations are now available: Gillette Stadium, Paycor Stadium, Hard Rock Stadium, Huntington Bank Field, and Northwest Stadium. Each named OSM stadium object has street/house-number and city tags matching the official address recorded in the preceding location audit. NWS point lookup confirms the expected state and provides an hourly forecast endpoint. Huntington's OSM state tag is absent; its state is corroborated by NWS and the operator address. Northwest's nearby NWS locality is Summerfield, while its official and OSM mailing locality is Landover; this is not treated as an address rewrite.

The points are the arithmetic midpoints of the stadium bounding boxes, explicitly not surveyed field centers. The OSM extracts, derived location database and map copies carry ODbL attribution. User-visible weather source details link the stadium map and ODbL notice. The location data is static; visitor traffic and scheduled weather refreshes do not query Overpass.

The first combined regex query timed out and returned an empty element list with a remark. It was not interpreted as an empty successful result. A bounded union of exact-name queries succeeded. Raw map and NWS point responses are archived by their decompressed SHA-256, with the acquisition manifest in `weather-map-pilot.json` and source license notice in `data/weather-location-sources/README.md`.

Coverage increases from nine to fourteen locations. The actual weather refresh returned five game forecasts, adding Tampa Bay–Cincinnati; the other new venues are outside the present collection window. Numerical model forecasts are unchanged.

Validation checks match official street/locality, preserve map-object identity, reproduce source hashes and bounds-midpoint arithmetic, reject changed addresses/coordinates, and bind NWS response geometry to the rounded requested coordinates. Independent adversarial review found no blocker and recommended that last coordinate-binding assertion, which was added. Five venue tests, seven weather tests and the production build pass. These are source and automated checks, not physical field measurements.
