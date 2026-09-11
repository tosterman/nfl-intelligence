# Odds attempt journal checkpoint

The new `recordAttemptEvent` module retains an immutable sequence for a single
acquisition attempt: reserved, requested, then captured or failed. Captured and
failed share one storage path, so conflicting outcomes cannot overwrite each
other. Records contain allowlisted fields only; provider errors, credentials and
request URLs are not serialized.

Every successor verifies its predecessors, including their exact canonical
bytes and chronological order. Repeating an identical event still validates the
predecessors. A lost write response is accepted only when an exact readback
matches the intended record. Invalid or missing evidence rejects the operation.

Eight targeted tests cover ordered persistence, field filtering, conflicting
outcomes, missing evidence, reversed chronology, lost responses, failed readback,
damaged predecessors and concurrent terminal writers. A regression reproduced
an unclassified TypeError for a stored JSON null; the reader now explicitly
rejects non-object predecessors. All 145 application tests and TypeScript
checking pass locally.

Independent AI code review found no material defect and reran all eight targeted
tests successfully. This is a bounded backend review, not a whole-product or
live-infrastructure certification. Create-only writes do not prevent a privileged
operator from deleting or replacing storage objects.

The initial module checkpoint was not connected to the collector or a schedule. Tests use an
in-memory immutable store; no live Blob writes or paid provider requests were
made. It does not prove that historical request coverage is complete, enforce
the account budget, or prove that an archive digest corresponds to a published
archive. Those remain responsibilities of the reservation, collector and
activation protocol. An interrupted producer can leave an attempt without a
known final outcome; that must not be interpreted as a refunded request.

## Collector integration

The collector now accepts an optional journal writer. Passing `recordAttemptEvent`
connects immutable evidence to the existing reservation, provider, publication and
readback steps. The production entry point does not enable it yet. The planned
adapter forwards this writer and rechecks eligibility immediately before paid
provider access, after awaited journal writes. It preserves the exact timestamp
passed to the authoritative reservation.

Reserved and requested events must finish before acquisition. Requested means
dispatch intent: interruption or an expired window can still prevent the network
call. Provider, storage and readback failures receive separate fixed reason codes.
A failure to journal a capture cannot produce a contradictory failed outcome.
If journaling itself remains unavailable, the caller receives an error and the
reservation remains consumed; missing outcome evidence is uncertainty.

Seven additional tests cover integration ordering, both pre-request journal
failure points, provider error filtering, uncertain capture evidence, reservation
expiry during journaling, real journal integration across five outcome scenarios,
and kickoff crossing during journal persistence. The kickoff regression initially
performed a paid request; the final pre-request eligibility check now defers it.
All 152 application tests and TypeScript checking pass locally. These tests use
in-memory provider and storage implementations and incur no paid acquisitions.

An independent AI code review of the integration found no material regression
and passed all 33 targeted collector, planned-collector and journal tests. The
review confirmed that requested records cannot establish completed request counts:
a final timing rejection can leave dispatch intent with no paid request.

Next: establish authoritative history migration and exercise the actual hosted
storage before enabling journal writes and changing the operational schedule.
