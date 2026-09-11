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
