# Weekly matchup monitoring

The development branch adds `/api/matchup-status` and includes it as a sixth
read-only probe in the existing production health script. The route compares
the retained weekly sample with the site's season, week and season phase. It
checks collection chronology, source/schedule hashes, expiry and consistent
empty/nonempty sample states. A valid Week 1 empty sample is healthy; failed or
stale collection is HTTP 503. Responses disable caching.

The monitor independently checks the returned timestamps, scope, hashes and
counts before accepting HTTP 200, then retains identifying fields in the health
report. It does not acquire odds, send analytics events, recompute play counts or
establish model quality. Provider asset-derived expiry is supplied by the
validated acquisition artifact; this endpoint does not refetch the provider.

Evidence: 166 application tests passed before the phase check was added; the
targeted health test and all eight Python monitoring tests passed afterward.
TypeScript checking passed. The local HTTP endpoint returned 200/no-store and
its payload passed the production validator; exact readback is in
`matchup-health-local.json`. The HTTP failure drill preserves the failed forecast
attempts while verifying the other five feeds, including matchup context.

The new endpoint and sixth production probe must be released together. Neither
has been verified on the public deployment or an actual scheduled production run.

Independent review caught a false-green cutoff omission. Health, external
validation and the UI now reject invalid/noncanonical calendar dates and cutoffs
after source observation. Regressions cover malformed, impossible and future
dates. Targeted monitoring checks passed after correction.
