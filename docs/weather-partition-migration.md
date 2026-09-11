# Weather archive partition migration

## Decision and evidence

The current single-bundle implementation is a verified bootstrap, not an
accepted full-season storage design. One real additional collection grew the
archive from 137 to 151 observations and 126 to 141 source objects. The
presentation grew from 246,919 to 258,026 bytes. A linear four-collection/day
scenario reaches the object cap in about 32 days; this is an illustration,
not a growth forecast. See `reviews/weather-capacity.json`.

Independent architecture review recommends per-game immutable partitions.
Keep `WEATHER_RUNTIME_ENABLED` unset until this migration and public verification
are complete. Do not solve archive growth by raising caps or deleting history.

## Publication format

Use a versioned publication root referencing a compact current snapshot and an
immutable season index. The index maps each game ID to a partition hash. Each
partition contains that game's exact retained observations and the required raw
source hashes. Raw NWS response objects remain globally content-addressed.
Every referenced object has explicit byte size and SHA-256 verification.

Preserve completed-game partitions in the index. Keep observations with changed
kickoff or venue in their original contexts; existing eligibility logic decides
which may be compared. A later publication must retain previous index keys, and
every changed partition must prove exact append-only observation continuity.
Unchanged partitions keep their existing hashes.

Upload and verify new immutable objects first. Advance one publication pointer
with ETag compare-and-swap only after the full reference chain is valid. A
competing writer requires rereading and rebasing the proposed update; never
overwrite its pointer or accept history deletion. Failed uploads leave the prior
publication readable.

## Readers and workers

Homepage and health readers fetch the current snapshot only. A game-detail
reader retrieves that game's partition and checks it against the current game
and approved venue evidence. Past games retain access to their history. Keep
runtime schema, timestamp, size and hash checks at each object boundary.

The worker restores only the partitions for games it will collect and their
raw evidence. New source objects are uploaded once. It validates old and new
observations before replacing affected partition references. The publication
chain remains: root → snapshot/index → game partitions → original NWS bytes.

## Implementation and acceptance

1. Define bounded v2 object schemas and pure readers/validators with explicit
   separation between snapshot and per-game history.
2. Build a migration from the existing verified v1 archive. Prove every original
   observation and source reference survives exactly; retain the v1 archive.
3. Add append-only partition publication and pointer conflict handling. Test
   interrupted writes, uncertain write responses, concurrent updates, missing
   partitions, removed observations and removed index keys.
4. Change local homepage/health/game readers to scoped retrieval. Verify past
   game history after subsequent publications and kickoff/venue changes.
5. Change the worker to restore affected partitions and reuse immutable sources.
   Exercise a real isolated collection and measure requests/bytes as history grows.
6. Perform the controlled public reader rollout, verify exact public identity,
   then enable collection and observe a real scheduled run.

This migration must not change numerical forecasts, backfill publication
receipts, infer weather effects on scores, or introduce a new paid service.

## Implemented checkpoint

`scripts/weather_partitions.py` now builds and audits the offline partitioned
archive. The real migration preserves 137 observations across 14 game partitions
and 126 original compressed source objects. Snapshot size is 124,123 bytes;
the index is 1,585 bytes and largest partition 62,458 bytes. Four tests cover
exact deterministic migration, missing/corrupt objects, and rehashed attempts
to remove either a game or an observation. Independent review found no material
offline migration blocker. See `reviews/weather-partition-migration.json`.

Runtime readers, append-only publication, active-worker restoration, bounded
per-object validators and public cutover remain unfinished. A hash-valid object
alone is not evidence that its weather semantics or current context are valid.

The first scoped transport reader is now implemented in
`src/lib/weather-partition-store.ts`. Against the real migrated fixture it reads
the root and current snapshot in two object requests; adding one game's history
requires only the index and that partition. Four tests cover corruption, future
publication time, substituted game partitions, duplicate compact observations,
missing sources and mismatched compact values. Type checking passes. The reader
checks transport and ledger/history consistency; approved venue binding and
current snapshot semantics still need integration before any UI or live pointer
uses this format. It intentionally does not fetch raw NWS source bodies.

Current snapshot semantics now reuse the existing verified bundle codec. The
v2 snapshot embeds exact Python transport bytes containing current records,
their compact retained anchors, and current source references only. All full
histories stay in game partitions. Its size is now 180,577 bytes, replacing the
earlier transport-only 124,123-byte snapshot. Five scoped-reader tests pass,
including removed anchors, changed neutral-site context, invalid capture times,
and approved-venue binding. The existing v1 decoder regression and four Python
migration tests also pass. Type checking passes. Publication continuity and
live reader/worker integration remain pending.

`verify_partition_continuity` now compares publication time, preserved index
keys, exact Python-serialized observations and compact history, and original
source references. Unchanged partitions require only the two index/root pairs;
changed partitions are compared individually. Four continuity tests pass,
including valid append and removal/mutation rejection. Together with migration
tests, eight Python checks pass. Two separately replayed real collections also
passed: 137 → 151 observations, with all 14 games retained and the anchored
snapshot remaining 180,577 bytes. See `reviews/weather-partition-continuity.json`.
This is a continuity check, not a substitute for raw-source replay or pointer
publication verification; the publisher must enforce all three.

The storage transaction in `weather-partition-publication.ts` now verifies the
prepared root, snapshot, index, changed partitions and their referenced sources
before writing. It reuses exact existing immutable objects and advances a
version-conditional `weather/latest-v2.json` pointer only after readback. This
separate migration pointer preserves the v1 reader and archive until controlled
cutover; it is not a fallback that masks v2 failures. Four transaction tests and
five scoped-reader tests pass, including interrupted writes, lost responses,
concurrent publication, and missing source/index rejection before mutation.
The command-line publisher must still invoke Python source replay and continuity
verification before this storage transaction. No v2 storage publication occurred.

The command-line candidate pipeline is now connected. `publish_weather_v2.ts`
defaults to a read-only rehearsal; `--publish` is explicit. Preparation invokes
Python raw-source replay and migration audit, then verifies either actual stored
v1-ledger preservation or continuity against the prior v2 partitions. The real
rehearsal passed against the 137-observation published archive. See
`reviews/weather-v2-candidate-rehearsal.json`.

Independent review identified two cutover defects, now covered by regression
tests: an older candidate with the same ledger must be rejected, and a v1 writer
must not add history during v2 installation. Before publishing the first v2
pointer, the CLI conditionally freezes the exact v1 pointer. Updated v1 writers
reject its freeze flag; already-running writers lose their previous ETag. The
v1 data stays readable. All v1 writer code must include this guard before cutover.
If v2 publication fails after freezing, keep v1 frozen and resume the verified
migration; do not silently resume v1 writes. No live freeze has occurred yet.
The candidate and freeze regressions pass. The preceding full application run
passed 218 tests; it predates these final freeze/timestamp corrections.

## Live storage and local integration

On September 11 at 17:58 UTC, the reviewed v2 storage migration succeeded:
17 objects uploaded, 126 reused, all 137 observations preserved. The legacy
pointer is now frozen; it remains readable. The v2 publication is
`cfc430a9830f48dce53fac2d3dc8741598f27e40a3b65c9b7a25d94523c9ccab`.
GitHub listed no weather workflow and no local legacy publisher process was
running at cutover. See `reviews/weather-v2-storage-publication.json`.

Local readers now use only v2. The slate/health path fetches the current snapshot;
game pages fetch their own history against that same publication root. Health
reported 14/14 eligible games. A fresh 390px Atlanta–Pittsburgh and 1280px
Green Bay–Minnesota browser check confirmed current values and retained history,
with no page errors or horizontal overflow. The initial check saw one temporarily
missing section during local server update and was rerun after follow-up reads.
See `reviews/weather-v2-local-browser.json`. All 222 application tests and the
production build passed.

This is not a public website deployment. The v2 collection worker is still
unfinished; the existing gated workflow references v1 scripts and must be
updated before activation. Keep `WEATHER_RUNTIME_ENABLED` unset. Do not unfreeze
v1 or treat its frozen archive as the active update path.

The v2 scoped worker is now implemented. `collect_weather_v2.ts` creates an
isolated workspace, restores only indexed games whose kickoff is within seven
days, verifies their raw sources, collects NWS updates, builds and audits the
candidate, and checks continuity before optional publication. Untouched game
references are merged into the new index. If the publication changed during
collection, the worker aborts. Reports retain the failed stage without secrets.

A real collection rehearsal restored 137 observations/126 sources and prepared
151 observations/143 sources without storage mutation. The one-game integration
test verifies that restoring and publishing only Atlanta–Pittsburgh preserves
the full index, including all other game references. See
`reviews/weather-v2-worker-rehearsal.json`. The gated workflow now calls this v2
worker and retains its isolated evidence files. Keep activation disabled until
public rollout and exact public readback; a real v2 worker publication and an
actual scheduled run remain to be observed.

Hosted verification 34630872623 passed for `247dd19`, covering the prior complete
reader/migration checkpoint. The scoped-worker changes above are subsequent
local work and require their own hosted verification.

The first real scoped v2 worker publication succeeded on September 11 at
18:06 UTC. It restored all 137 prior observations, retained 151 observations
after collection, uploaded 33 objects and reused 126. The new publication is
`aec388f6440e093d9f144d35ea596b1851bc32f7ed1ec5085a5582b437d964f7`.
Local health initially returned the prior cached version, then returned this
exact publication with 14/14 eligible games after 15 seconds. No site rebuild
was performed. Evidence: `reviews/weather-v2-worker-publication.json` and
`reviews/weather-v2-worker-local-readback.json`. Public deployment, exact public
readback and an actual scheduled run remain unverified; keep the workflow gate
disabled until those rollout prerequisites are met.

Hosted run 34631754560 passed on `b673d2e`, covering the scoped-worker batch and
retained live publication evidence. Its application suite contains 223 tests;
hosted verification also covers Python tests, replay, browser deadline checks,
production build and dependency audit. Later homepage/personnel work is separate.
