# Venue map source attribution

OpenStreetMap data in the archived Overpass responses, `../weather-osm-venues.json`, and map-element copies in weather snapshots is © OpenStreetMap contributors, available under the Open Database License (ODbL) 1.0: https://www.openstreetmap.org/copyright . The derived stadium bounding-box midpoints and address reconciliation are published with the same ODbL terms. This notice applies to that map data, not the application's code or unrelated source datasets.

Files are gzip-compressed raw responses named by SHA-256 of the decompressed bytes. The venue records distinguish map-source hashes from NWS point-response hashes. NWS responses are US government weather data. Map geometry is not a survey or a stadium field sensor. The map query was a bounded acquisition; the live application makes no requests to OpenStreetMap or Overpass.

The archived response `59fbcc5911e00df54b9be6d65b5299cf205aac3b78de6536120efc21b387f946` contains a timeout remark from an initial regex query and is retained only as failed acquisition evidence. It supplies no production coordinates. The subsequent exact-name query produced the accepted map data.
