# Independent personnel publication

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
