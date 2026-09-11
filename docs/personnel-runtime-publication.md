# Independent personnel publication

The current panel imports build-time injury, quarterback, participation and
report-change artifacts. Refreshing only the injury file would leave the others
bound to an older source. The runtime change must publish a compatible set and
preserve the existing identity, freshness and pregame cutoffs.

## Publication unit

One immutable publication root selects a current presentation object containing
personnel, quarterback roles, both collection states, prior-season usage,
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
5. Retain immutable objects, verify readback, then conditionally move the pointer.
   A concurrent publication requires recollection/revalidation. Preserve all
   previous history references; never rewrite an old observation.
6. Check the exact new root through local health and browser rendering without a
   build. Then verify the deployed reader and one real scheduled collection.

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
This does not yet prove normalized quarterback replay, fresh acquisition,
failure handling, storage publication or runtime behavior.
