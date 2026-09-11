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

Scheduled integration is pending. Before wiring it, update fixed-vintage UI
regression tests so legitimate future source revisions are checked against their
own retained evidence, rather than required to reproduce a superseded vintage.
Also retain the new artifact and collection record in publication/recovery paths.
No hosted refresh or deployment was performed in this checkpoint.
