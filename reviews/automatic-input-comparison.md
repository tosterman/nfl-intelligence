# Exact bundle comparisons during refresh

The staged refresh workflow remembers the exact site-file hash before acquisition.
After verified input retention, it resolves the before/after manifests by those
site hashes, restores both bundles, and compares matching CSV sources by record
identity. New and removed source files are listed separately. An incompatible
CSV schema requires an explicit migration rather than a misleading comparison.

Comparison reports are immutable and content-addressed under
`data/forecast-input-archive/comparisons/`. They name both manifest identities,
edition times and site hashes, and contain added/removed/revised records. They
do not establish original source availability or numerical forecast causality.
Reversed or timezone-free edition timestamps are rejected.

Missing older inputs yield an explicit unavailable report. Current inputs must
still restore and validate; a missing or corrupt current bundle fails. Review
found the original missing-prior branch skipped that validation. A regression
failed before the fix and passed afterward; independent review confirmed the fix.

Five targeted tests cover ordered exact comparison and repeatability, unavailable
or undated inputs, pre-refresh identity binding, added source separation and
corrupt-current rejection when older history is absent. A full Python run passed
283 tests before the final regression was added; all five final targeted tests pass.

The real local remember/finish path compared the current retained edition with
itself: 18 files, no source changes, comparison hash
`641e363619083ad0e7d2fe746dedb4bafc728ce8ce976e47d05a75fc1798fc57`.
This checks the real bundle path without fabricating a new refresh. Distinct
edition comparisons were exercised with controlled fixtures. No data acquisition,
model modification, public deployment or live workflow execution occurred.

The UI still consumes its single verified historical source pair. Selection and
presentation of new comparison reports in forecast history is the next step.
