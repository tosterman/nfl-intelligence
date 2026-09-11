# Reading acquisition evidence

`readAttemptEvidence` reads the three immutable slots for one attempt, newest
first, then validates the visible event's entire predecessor chain. It rejects
unknown schemas, foreign attempt identities, wrong slots, oversized or
noncanonical bytes, missing predecessors and reversed event times. Storage
failures propagate rather than becoming an empty history. No writes occur.

Missing evidence returns null. A reservation alone does not prove a provider
request. Requested means dispatch intent; a captured digest still needs archive
verification. A concurrent append can leave this read reporting an earlier valid
stage. This reader therefore does not establish latest status or complete usage
coverage and is not connected to the planned collector's activation policy.

Validation: three new tests failed before implementation; all 11 journal tests,
all 161 application tests and TypeScript checking then passed. An independent
adversarial review found no material defect. A local Node process read the prior
isolated private Blob probe, verified all three retained SHA-256 values, and
correctly recovered its synthetic unknown-error outcome. Exact evidence is in
`odds-journal-reader-verification.json`. No provider request or storage write
was needed for that check.
