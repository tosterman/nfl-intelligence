# Default collector audit wiring

The existing API entry point imports `collectOdds`, which now passes
`recordAttemptEvent` to `runOddsCollection`. This connects the already tested
immutable journal to ordinary acquisitions when the development branch is
released. The planned collection adapter remains disconnected.

Validation: all 165 application tests and TypeScript checking passed. Existing
collector/journal integration tests cover success, provider/storage/readback
failure, uncertain terminal persistence, reservation retention, concurrent
attempts, and no reacquisition after an ambiguous outcome. The entry-point wiring
was inspected directly. No provider call, live reservation, paid plan change or
deployment was performed for this change.

This adds private Blob reads/writes to future acquisitions. Journal availability
is intentionally required before provider dispatch. An interruption can still
leave only an atomic reservation or dispatch intent; these are not evidence of
zero usage or a known provider outcome. The historical migration, authoritative
writer policy, hosted validation and sustained scheduled-run evidence remain
required before activating the planned budget-aware executor.
