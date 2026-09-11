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

This module is not yet connected to the collector or a schedule. Tests use an
in-memory immutable store; no live Blob writes or paid provider requests were
made. It does not prove that historical request coverage is complete, enforce
the account budget, or prove that an archive digest corresponds to a published
archive. Those remain responsibilities of the reservation, collector and
activation protocol. An interrupted producer can leave an attempt without a
known final outcome; that must not be interpreted as a refunded request.

Next: connect event persistence to the experimental collector, inject failures
at every boundary, and preserve consumed reservations even when evidence storage
fails. Activation still requires an authoritative history migration and hosted
storage verification.
