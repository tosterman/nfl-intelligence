# Weather venue location provenance — 2026-09-10

`data/weather-venues.json` maps eight exact current schedule venue strings to operator/public-owner addresses and US Census geocoding evidence. **Four addresses resolved uniquely; four remain unavailable.** No team-home fallback, bulk stadium-location dataset, or guessed coordinates were used.

These coordinates are **address-interpolated vicinity points**, not surveyed playing-field centers. Use them to obtain an explicitly labeled stadium-vicinity NWS forecast. They do not describe wind within the stadium bowl. Venue identity must match the actual scheduled venue; this mapping must never substitute Los Angeles home coordinates for the Melbourne neutral-site game.

| Exact venue key | Latitude | Longitude | Address source |
|---|---:|---:|---|
| Bank of America Stadium | 35.225780031248 | -80.850875963353 | [Panthers stadium booking](https://www.panthers.com/stadium/booking) |
| Nissan Stadium | 36.166985485846 | -86.773987270280 | [Nashville Sports Authority](https://www.nashville.gov/departments/sports-authority/nissan-stadium) |
| Lincoln Financial Field | 39.904449230665 | -75.166688629533 | [Operator FAQ](https://www.lincolnfinancialfield.com/faqs/) |
| GEHA Field at Arrowhead Stadium | 39.048923084936 | -94.486488590578 | [Chiefs stadium guide](https://www.chiefs.com/stadium/atozguide) |

Lincoln Financial Field's operator specifically directs navigation users to **1020 Pattison Avenue**, which was geocoded. Its mailing address was not silently treated as a GPS location. Nissan Stadium's address is confirmed by its public owner, the Nashville Sports Authority, as One Titans Way.

The following verified operator addresses returned zero Census matches and have no latitude/longitude fields:

- Acrisure Stadium: 100 Art Rooney Avenue, Pittsburgh, PA 15212. [Official parking/traffic guide](https://acrisurestadium.com/wp-content/uploads/guides/acrisure-stadium-parking-and-traffic-guide.pdf). The operator's directions page embeds the same address, which does not resolve the Census match failure.
- EverBank Stadium: 1 EverBank Stadium Drive, Jacksonville, FL 32202. [Operator contact](https://everbankstadium.com/contact).
- MetLife Stadium: 1 MetLife Stadium Drive, East Rutherford, NJ 07073. [Operator A–Z guide](https://www.metlifestadium.com/a-z-guide).
- Paycor Stadium: 1 Paycor Stadium, Cincinnati, OH 45202. [Bengals contact](https://www.bengals.com/fans/contact).

Each JSON entry retains its exact request URL, retrieval timestamp, official address source, Census matched address and full address match object. The Census query uses the one-line address endpoint with `Public_AR_Current`; results were fetched on September 10, 2026. A current benchmark can change later, so preserve this evidence rather than assume future requests reproduce the exact coordinate. [US Census Geocoding API documentation](https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html).

Validation: all eight keys exactly match Week1 schedule venue strings; the four successful responses each contain exactly one address match with US latitude/longitude, and failed matches have coordinates omitted. Data schema: exact venue key → `latitude`, `longitude` when available, plus `address`, `addressSource`, `geocodeSource`, `coordinateMeaning`, `retrievedAt`, `status`, and retained response evidence. NWS acquisition, forecast freshness, kickoff matching and user-facing display are separate checks handled by the publishing pipeline.
