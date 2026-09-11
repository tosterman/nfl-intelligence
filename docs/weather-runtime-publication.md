# Independent weather publication

Capacity finding: the verified v1 bootstrap accumulates all history in each
bundle and is not suitable for a full season. Before enabling scheduled
collection, complete `docs/weather-partition-migration.md`. Keep the existing
archive and freshness checks intact during migration.

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
streams. The first real publication succeeded on September 11 at 17:24 UTC:
128 objects retained 137 observations. Local runtime integration subsequently
served all 14 eligible games. The current public site still reads its static
weather edition; storage publication is not public deployment evidence.

The recovery worker restores and replays retained history before collection.
The new `weather.yml` workflow runs every six hours only when the repository
variable `WEATHER_RUNTIME_ENABLED` equals `true`. Leave that variable unset until
the public runtime reader has been deployed and verified. The workflow restores,
collects, replays, publishes, then checks public freshness and exact manifest and
generation identity, allowing 90 seconds for the reader cache to refresh.
It retains collection and readback evidence and fails on unavailable coverage or
a mismatched public bundle. Real Blob recovery into an empty local folder passed
on September 11 at 17:33 UTC: all 137 observations and 126 source files replayed,
and a repeated restore preserved identical ledger bytes. Evidence:
`reviews/weather-fresh-worker.json`. The first scheduled run and public rollout
still require verification before calling this operational.

The isolated collection rehearsal then used the committed stadium-location
evidence and real NWS requests. It retained the prior 137 observations, added 14,
and prepared a verified 143-object bundle with 14 available games. The copied
model edition remained byte-identical. No storage publication was attempted in
this rehearsal. See `reviews/weather-collection-worker.json`. Fresh workers need
both the restored weather archive and the committed `weather-location-sources`
directory; the normal GitHub checkout supplies the latter.

The active local storage implementation has since moved to per-game v2 history
partitions; see `docs/weather-partition-migration.md`. The legacy pointer is
frozen and must remain so. The gated workflow now runs `collect_weather_v2.ts`,
which restores only upcoming games and preserves untouched game references.
Its first real publication at 18:06 UTC retained 151 observations, and localhost
read back the exact new version with 14/14 coverage without rebuilding. This
confirms the local update path; public rollout and scheduled execution are still
pending. Do not activate the workflow based on local evidence alone.
