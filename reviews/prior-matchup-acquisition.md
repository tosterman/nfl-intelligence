# Prior-season acquisition checkpoint

The standalone `python -m scripts.refresh_prior_matchup` command derives the
prior season from the current site's season. It reads provider metadata, checks
asset identity, size and SHA-256, preserves source bytes and manifests, and runs
the shared completed-game validation. Historical play-by-play may be older than
30 hours; the schedule must still be updated within 30 hours. Future source
timestamps remain invalid. Previously retained play-by-play bytes are reused
only after metadata size and digest verification.

A failed acquisition writes a separate collection failure record and preserves
the last verified historical artifact. The UI rejects an artifact for another
forecast season. A failed collection must not be described as a successful
refresh merely because historical data remains displayable.

The real collection started at 2026-09-11T15:06:39.053901Z and succeeded, producing
manifest `0b53248063830e4240a734ae0c6dd441223cf8efc0577b31f0aafe5fb76f068e`
and artifact `a8cb653e80978bbbca5dac9aedd37839756b4700c4be09298c40cf0a54e27a16`.
The two historical UI checks still pass against every previous displayed count.
The original four current-season acquisition tests pass after the shared
collector change. Historical tests cover cache reuse, stale schedule rejection,
corrupt cached bytes, preservation after failure and exact retained-input replay.

The development workflow now invokes the historical collector independently of
weekly collection. Git publication and recovery artifacts retain both the
accepted sample and collection outcome. Fixed-vintage UI regression tests use an
immutable archived snapshot; current captures are replayed against their own
source manifest rather than required to match a superseded vintage. The panel
components accept evidence explicitly for these tests and use retained current
evidence by default in the application.

The production workflow remains disabled pending release recovery. No actual
scheduled historical refresh or hosted deployment has been verified.

Integration validation: all 304 Python tests passed. All 168 TypeScript tests
passed before the final fixture-injection edits, followed by all 11 affected
panel/selector tests passing. TypeScript checking also passed after component
fixture injection. Expected simulated acquisition failures in the Python test
output are part of failure-path coverage, not successful live collections.
