# Independent personnel publication

Current checkpoint: private storage and the local runtime reader are active.
A fresh worker can restore and replay the accepted current source closure.
Recurring acquisition/derivation/publication and public scheduled operation are
still unfinished. The sections below retain the implementation chronology.

The current panel imports build-time injury, quarterback, participation and
report-change artifacts. Refreshing only the injury file would leave the others
bound to an older source. The runtime change must publish a compatible set and
preserve the existing identity, freshness and pregame cutoffs.

## Publication unit

One immutable publication root selects a current presentation object containing
personnel, quarterback roles, all three collection states, prior-season usage,
current-season participation, report changes and exact game contexts. Include
the source and acquisition identities that existing selectors already require.
Bind season, phase, week, teams, kickoff, venue and neutral status to the deployed
game before exposing current context. Read one root per render so nested panels
cannot mix versions. Keep numerical forecasts unchanged.

Retain raw evidence separately. Quarterback sources already use deduplicated
compressed timestamp chunks and reconstruction manifests; preserve those bytes.
Retain injury captures and their source files, participation source files,
registry evidence, schedule bytes and the audits used to derive presentation.
Do not package cumulative raw history into a reader response. An immutable
publication links its predecessor and evidence references; a worker restores
only inputs required for the next verified transition. Historical retrieval
must remain bounded and must not require loading the entire season on a page.

## Worker sequence

1. Restore the selected publication and required source objects into an isolated
   directory; verify hashes before use. Pin the exact schedule and registry.
   Require the schedule digest declared by the selected edition to match the
   actual schedule bytes, in addition to matching each deployed game context.
2. Collect injury, depth-chart and participation sources independently. Preserve
   prior valid snapshots and original dates on failure; record failed collection
   state explicitly. Failure must not turn missing evidence into healthy players,
   confirmed starters or zero participation.
3. Replay injury captures, reconstruct quarterback raw chunks, verify normalized
   roles, rerun the identity audit, and rebuild prior/current participation from
   source bytes. Rebuild report differences against the retained predecessor.
4. Validate exact input bindings and all presentation references. If the identity
   audit cannot establish a common cutoff, withhold dependent usage explicitly;
   do not copy a successful audit from the previous report into the new one.
   This is an explicit degraded-publication branch: retain available dated
   reports and all three collection states while marking incompatible derived
   usage unavailable. A derivation exception must not prevent a failed-collection
   status from becoming visible. Keep acquisition, identity-audit and participation
   cutoff timestamps distinct from the new publication timestamp.
5. Retain immutable objects, verify readback, then conditionally move the pointer.
   A concurrent publication requires recollection/revalidation. Preserve all
   previous history references; never rewrite an old observation.
6. Check the exact new root through local health and browser rendering without a
   build. Then verify the deployed reader and one real scheduled collection.

The runtime transition builder must operate on the accepted injury capture and
its predecessor, rather than call the cumulative `personnel_changes.py` scan.
The offline probe currently copies full retained directories; that is a bootstrap
feasibility check, not the intended recurring restore algorithm. Preserve older
immutable transition references without rebuilding their payloads.

## Required verification

- Fresh worker reconstruction from retained evidence before network collection.
- Missing/corrupt source or chunks, changed identities, source cutoffs, schedule
  changes, mixed presentation versions, future timestamps and expiry at kickoff.
- Failed collection with dated retained reports and explicit unavailable derived
  usage; no fabricated no-change event when comparison evidence is missing.
- Interrupted uploads, lost responses, concurrent publishers and replay against
  a changed predecessor, with previous publication still readable.
- Injury panel, compact briefing, full participation disclosures, report changes,
  quarterback roles and health must all consume the selected runtime publication.
- Browser interaction at mobile/desktop sizes and exact worker-to-reader update
  without a rebuild. Public deployment and scheduled operation are separate proof.

Implementation is not complete. `scripts/rehearse_personnel_worker.py` is the
offline reconstruction probe; it neither collects sources nor publishes storage.
No existing static imports or public behavior have been removed at this stage.

The first probe passed on September 11 at 18:14 UTC: 322 copied input files
(16,349,527 bytes, including scripts) remained unchanged. Five pipeline steps
rebuilt report changes and both usage artifacts, each with 139 report records.
See `reviews/personnel-worker-rehearsal.json` for the exact input inventory.
The subsequent 18:15 UTC probe additionally reproduced normalized quarterback
roles from the retained raw source at the original acquisition time. It still
does not prove fresh acquisition, failed-collection publication, schedule/edition
binding rejection, bounded recurring restore, storage publication or runtime
behavior. Those remain required implementation checks.

At 18:16 UTC the isolated probe passed with the new `personnel_schedule.py`
gate: the edition's declared source digest matched the schedule bytes and all
272 game contexts matched. Four regressions reject changed bytes, altered
contexts and missing/duplicate scope. The numerical engine was not modified.

`personnel_transition.py` now replays just the explicitly selected previous and
current injury captures. Four regressions verify agreement with the existing
retained change presentation without an archive scan, an initial unknown
comparison, and rejection of invalid/missing/reversed/unchanged captures. The
runtime publisher must supply the accepted predecessor and retain previous
transition references; this helper alone does not prove archive continuity.
Independent review found no material helper defect and reran the eight new
tests. The publisher must bind the current capture to its selected personnel
snapshot, bind the predecessor to the accepted publication, and permit a null
predecessor only for an explicit initial/season baseline. Failed collections
retain the existing transition; identical captures are not a new observation.
All 28 personnel Python tests passed locally at this checkpoint.

## View integration preparation

The panel now accepts one `PersonnelEvidence` value and passes its selected
quarterback, history and participation artifacts through every nested view.
Those views no longer import independent data files. A temporary static adapter
still supplies the current edition at the panel boundary; no live storage reader
has been activated. The three collection states are represented in the type,
but participation collection failure rendering still requires implementation.

Four injected-data regressions cover compact and full disclosures, incompatible
evidence without static fallback, and complete-panel propagation. Independent
review found no material regression. All 230 application tests, type checking
and the production build passed.

The initial populated-page browser check could not find the full reports: the
retained personnel and quarterback assets had passed their 30-hour deadline
(September 10 at 12:03 and 12:01 UTC respectively). A follow-up check confirmed
the explicit expired state, keyboard source disclosure, no horizontal overflow
and no scoped accessibility violations in Chromium/WebKit at 320/1280px.
`reviews/personnel-props-browser.json` records that scope. It is not a successful
populated live-page check; populated behavior is presently covered by injected
render tests. Fresh collection and runtime publication remain outstanding.

Hosted verification 34632254746 passed on `a1f6643` (the homepage and earlier
offline rehearsal checkpoint). The schedule/transition and view-injection work
above came afterward and needs its own hosted verification.

## First fresh collection candidate

The isolated `--collect` rehearsal succeeded on September 11 at 18:23 UTC.
All three collectors exited successfully. The injury asset was updated at
12:12 UTC and the depth-chart asset at 12:22 UTC that day; both were acquired
after 18:22 UTC. Reconstructed quarterback roles matched their source bytes.
The derived artifacts cover 167 reports and 49 observed report changes; the
participation source still has 187 rows. All 272 edition game contexts matched.
See `reviews/personnel-collection-rehearsal.json` for source identities and
the retained candidate directory.

The copied model/schedule and existing archive files remained unchanged. Current
source pointers and collection states were intentionally refreshed only inside
the isolated directory. The report's `inputsUnchanged` checks pinned and archived
inputs, excluding those mutable pointers during collection. No candidate files
were promoted to the site and no storage publication occurred. This rehearsal
still uses cumulative bootstrap history and does not implement failed-derivation
publication.

The panel now also exposes failed participation collection outside report expiry
wrappers, so that failure remains visible when the reports are already outdated.
A regression explicitly supplies expired reports and a failed participation state.

Hosted run 34632870555 failed in the new schedule tests: CI's source preparation
downloads a current `games.csv`, which can differ from the retained edition.
The tests now decompress the immutable schedule object named by that edition's
source hash. The production validator remains strict. All four corrected schedule
tests passed locally; a broader Python rerun is in progress. This failed hosted
run is not launch acceptance evidence.

The corrected full local Python suite subsequently passed all 365 tests. The
correction and fresh-collection checkpoint were pushed as `fae7533`.

## Presentation assembly

`personnel_presentation.py` now assembles previously replayed artifacts into one
bounded presentation, with exact schedule contexts, original source timestamps,
all three collection states and explicit derived-evidence status. It rejects
mixed report history and participation inputs. Incompatible injury/depth-chart
cutoffs preserve dated reports and collection states while withholding both
derived participation artifacts. Failed participation acquisition labels usable
retained participation as retained without changing its source date.

Independent review caught a missing cross-artifact identity binding. The assembler
now checks the identity audit against exact personnel and quarterback bytes, then
binds historical and current participation to that audit using their existing
producer hash contracts. Historical audit hashes use original bytes; current
participation uses LF-normalized repository metadata. External source bytes are
not normalized. A replaced-quarterback regression verifies rejection.

All 34 personnel Python tests pass, including six assembly cases. The fresh real
candidate assembled at 18:30 UTC into 505,796 bytes covering 167 reports and 272
game contexts. `reviews/personnel-presentation-candidate.json` records its hash.
This module validates compatibility, not raw-source calculations: publication
must first replay normalization and derivation, retain the exact source/audit
objects, validate reader schema and verify immutable storage and pointer updates.
Those publication and reader steps remain unfinished.

The follow-up independent review confirmed the audit-binding fix and reran all
six assembly tests. Hosted run 34633367418 passed on `fae7533`, covering the
preceding fresh-collection and corrected-fixture checkpoint; assembly is newer.

## Reader validation

The TypeScript presentation decoder verifies the exact object hash/size, schema,
timestamps, game contexts, collection states, report scope, safe quarterback
source URL and report-change structure before a component receives the object.
It rejects duplicate player scope even when names differ. The game selector
requires every declared context field to match the page's game. Derived usage
must bind to the selected report snapshot and contain the same player identities;
its nested values still pass through the existing fail-closed usage selectors.
Reader acceptance alone does not prove raw-source or numerical replay.

Five decoder tests and type checking pass. Independent review reran the tests
and found no material rendering blocker. The actual isolated 505,796-byte Python
candidate decoded successfully with 167 reports and 272 contexts; evidence is in
`reviews/personnel-reader-candidate.json`. This decoder is not yet wired to the
live page. Storage transaction, archive retention and runtime health integration
remain required before replacing the static adapter.

## Storage transaction

The personnel transaction now validates its immutable root/presentation and all
declared archive objects before any write. New roots link the accepted previous
root. The writer verifies immutable readback before an ETag-conditional pointer
switch, preserves competing writers, and accepts uncertain responses only after
readback. An identical retry performs no writes. Acquisitions cannot regress;
equivalent timestamp representations cannot conceal a different source hash at
the same acquisition time. The reader fetches only pointer, root and presentation.

Five transaction tests pass, including upload interruption, missing evidence,
lost responses, concurrency, predecessor linkage and equivalent time formats.
The private Blob adapter restricts writes to the personnel namespace and applies
the existing bounded-stream/timeout behavior. Independent review confirmed the
timestamp correction and adapter rules; its path regression and type checking
also pass. An actual read-only Blob check found no personnel publication.

The transaction bounds a candidate to 64 MB, 5,002 provided objects, 10 MB per
object, a 1 MB root and 5,000 archive references. These are rejection limits,
not evidence that recurring collection fits indefinitely. The complete archive
selector, source replay integration, fresh-worker restore and initial real
publication still need implementation. The transaction cannot infer whether a
caller omitted a required source; source/archive closure remains a publisher
responsibility. No real personnel storage writes have occurred.

All 242 application tests passed locally after the storage/reader batch.

## Initial private publication and local activation (September 11, 18:50 UTC)

This checkpoint supersedes the unfinished bootstrap/runtime statements above.
The isolated candidate was independently replayed with its retained scripts at
the recorded calculation times. Quarterback reconstruction also runs inside
that isolated candidate. The exact 471-file inventory remained unchanged.
`personnel_archive.py` packages that proof, source files and packaging code;
`publish_personnel_bootstrap.ts` validates all local object bytes, rehearses the
transaction in memory, then optionally publishes with `--publish`. This is an
initial bootstrap command: an existing different publication is rejected.

Private publication `c3cdbbda3af5af0324485935370b7de3d081e729ca9f6a9c65e465117c8ed8a7`
uploaded and read back 477 objects (26,470,601 bytes), with 475 archive references
and 167 report records. The accepted root has no predecessor. See
`reviews/personnel-candidate-replay.json`, `reviews/personnel-bootstrap-package.json`
and `reviews/personnel-bootstrap-publication.json`.

Matchup pages now read that publication through a 60-second server cache and
require exact game-context matching. Both forecast and pending-forecast paths
pass the same evidence into nested views. Missing or invalid publication data
renders an explicit unavailable state; source-age expiry still applies.
The three personnel/QB/participation health routes use the selected runtime
publication. Participation health additionally verifies its archived source
object. Populated browser checks passed at 320/1280px in Chromium and WebKit,
including keyboard disclosures, separate seasons, no horizontal overflow and
zero scoped axe violations. These are local checks, not public rollout proof.

Still required: bounded recurring-worker restore and publication, failed-source
refresh handling, scheduled execution, public deployment/readback and real
weekly participation rollover. Initial archive capacity does not establish
indefinite growth safety. The bootstrap command trusts the controlled local
replay/packaging process; it is not an untrusted-upload endpoint.

## Bounded current-source restore

`restore_personnel_worker.ts` restores the accepted publication into a new local
directory using hash-verified, create-only files. It selects current injury and
QB captures, the current participation source, only the QB manifest's referenced
chunks, pinned schedule/registry evidence, collection states, derived artifacts
and retained scripts. Older injury captures and cumulative change ledgers are
not restored. Their accepted publication remains in immutable storage.

The restore binds selected artifacts and exact game contexts to the reader
presentation, checks schedule bytes, verifies decompressed source hashes and
reconstructs the QB source hash in manifest order. Existing capacity ceilings
remain rejection limits. Retaining the complete current provider QB source can
still grow as the provider file grows; this is not constant-size storage.

Actual private restore selected 321 files (17,683,952 bytes) from 475 archived
logical files. Its retained scripts reproduced 167 player reports and 32 listed
QB team contexts, and verified all 272 schedule contexts. See
`reviews/personnel-runtime-restore.json` and
`reviews/personnel-restored-source-replay.json`. Two regressions cover selective
restoration and missing/corrupt inputs; independent review found no material
restore blocker. This does not establish new acquisition, derived usage replay,
failed-source publication or repeat scheduled operation.

## Isolated recurring refresh candidate

`refresh_personnel_worker.py restored-directory --collect` copies a restored
worker and attempts all three collectors. Nonzero exits, including timeouts,
restore the original source pointer bytes and write an explicit failed collection
state. The current injury capture is compared only with the accepted capture;
an unchanged capture retains the prior change presentation. Source normalization
and QB reconstruction run using the retained worker scripts before derivation.

Identity and participation steps stop at the first failed derivation. The
assembler can explicitly withhold both usage artifacts while preserving reports,
their original dates and collection failures, including when a failed calculation
left truncated JSON. This branch still enforces schedule, history, source-season
and chronology checks. Integrity conditions use explicit exceptions, so Python
optimization cannot disable raw reconstruction or QB role comparison.

The September 11 18:57 UTC real isolated refresh collected all three sources and
completed all four derivation steps with 167 reports. Corrected source checks
were rerun against that candidate. Eleven targeted regressions cover rollback,
dependency failure, withholding, binding and optimized-mode QB tampering. See
`reviews/personnel-runtime-refresh.json` and `reviews/personnel-refresh-recheck.json`.
This remains an unpublished candidate: independent derived replay, incremental
archive packaging, predecessor-bound publication and live update readback remain
required. The candidate's source and calculation times must not be rewritten.
