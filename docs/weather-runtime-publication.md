# Independent weather publication

## Why

Scheduled health run 34623950366 detected expired public weather while the
forecast publisher was paused for a provider build limit. Weather refreshes
should not require numerical forecast changes or a site build. This design needs
one initial deployment; it cannot update the currently deployed static reader.

## Existing capabilities verified

- Private Blob reading, immutable archives and version-conditional pointer writes
  exist in `src/lib/odds-store.ts`.
- GitHub Actions already has `BLOB_READ_WRITE_TOKEN`; secret values were not read.
- Python collection retains raw NWS responses, and `weather_history.py` replays
  their point-to-forecast linkage, timestamps, measurements and venue evidence.
- Current retained source material is 126 compressed files totaling 476842 bytes.
  Snapshot/history/ledger total approximately 675KB before compression. Runtime
  readers should fetch compact presentation data, not the full source archive.

## Implementation sequence

1. Build a weather-only bundle from verified Python output. Retain immutable
   raw source objects plus snapshot and compact history; a manifest binds hashes,
   acquisition times, approved venue registry identity and per-game context.
   Use explicit schema/validator versions. Numerical snapshots remain untouched.
2. Upload immutable objects and verify readback before advancing a weather-only
   latest pointer with ETag comparison. Equal timestamps with unequal hashes
   conflict; older collections cannot replace newer ones. Recover uncertain
   writes by comparing exact retained bytes, never by overwriting blindly.
3. Implement a server-only reader with bounded sizes, decompression, timeouts,
   hash checks and caching. Select a single bundle per request. Never acquire
   NWS data on a page view or relabel a cached acquisition as newly collected.
4. Replace static weather imports in slate, game context, revision brief,
   history and health with that common selection. Require the deployed schedule's
   game ID, season, kickoff, venue and neutral status to match. Approved venue
   registry compatibility must be checked; runtime input cannot introduce new
   location methods or arbitrary coordinates.
5. Add a separate scheduled collection/verification/publication workflow using
   existing storage. Restore retained history before collection so a new worker
   cannot drop past issues. Keep it inactive until the runtime reader is deployed
   and the controlled publication succeeds.

## Acceptance and failure cases

- Snapshot and history become visible atomically through one manifest.
- Failed/missing/corrupt objects and incompatible versions fail explicitly;
  no silent static fallback that disagrees with monitoring.
- Upload interruption and uncertain responses preserve the prior verified
  pointer; concurrent writers cannot regress acquisition time or lose history.
- Changed kickoff, season, neutral status or venue evidence withhold context.
- Empty eligibility differs from collection failure; partial coverage remains
  visible. Existing 30-hour checks and browser expiry remain intact.
- After initial deployment, a controlled storage publication changes page
  weather and health without another deployment. Retain exact readback evidence.
- Storage retention alone never proves historical public availability.

Independent architecture review supports this bounded weather-only change before
rollout. Implementation is in progress: the Python bundle builder replays retained
sources and binds schedule/venue context; storage primitives verify immutable
objects before conditional pointer publication; the reader validates hashes and
can select presentation objects without downloading raw archives. Three Python
bundle tests and eight TypeScript storage tests pass, including corruption,
interrupted writes, concurrent publishers and bounded stream reads.

The private Blob adapter uses the existing credential, create-only archives,
ETag-conditional pointers, five-second request timeouts and bounded response
streams. A real read of `weather/latest.json` succeeded and returned absent; no
weather storage writes occurred. The adapter accepts only weather namespace
paths. Live weather-specific publishing, retained-history continuity, runtime
schema/context validation, page integration and scheduled activation remain
unfinished. The current public site still reads its static weather edition.
