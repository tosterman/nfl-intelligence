# Participation feed health — September 11, 2026

`/api/participation-status` reports acquisition freshness and binding between the
current participation source, collection outcome, generated artifact and personnel
report. It fails at 30 hours, on failed collection, mismatched source/report or
season, and inconsistent/future timestamps. An empty eligible Week 1 sample is
not itself unhealthy: this route does not claim complete coverage or availability.

The production monitor includes the route and independently checks timestamps,
season, source identity and row count. It retains acquisition/calculation/report
times and collection status with the probe. The release bundle includes the two
source/collection metadata files used by the route.

Two TypeScript tests and nine Python monitoring tests passed, including a local
HTTP failure drill. At 16:46:58 UTC the real local endpoint returned HTTP 200;
the monitor independently accepted its source hash, 187 source rows, 16:32 UTC
collection and 16:34 UTC calculation. The production build passed with 319 pages.

The new route and seven-feed monitoring set are not yet publicly deployed. The
currently running main-branch monitor retains its earlier endpoint set until the
reviewed release reaches main. No odds acquisition or analytics event was sent.
