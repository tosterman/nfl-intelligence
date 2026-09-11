# Prior-season release review

The local production build completed successfully, including all 319 generated
pages. GitHub CI for ba51d89 also completed successfully; later changes still
require their own CI result.

Review found two recovery issues:

- The historical replay command could replace the current artifact while leaving
  its collection receipt unchanged. It now writes only a review artifact. A real
  optimized-Python replay reconciled all 285 games and 32 teams. Before and after
  execution, the live artifact SHA-256 remained a8cb653e80978bbbca5dac9aedd37839756b4700c4be09298c40cf0a54e27a16
  and collection record remained e00fdf91ba7f4776da376d76df6dfe9dcc5e13b9777e6f4d47d18fc4be1b1715.
- Independent adversarial review identified misleading failure reporting if the
  sample update succeeded but collection receipt persistence failed. This now
  reports the partial outcome and updated artifact digest, instead of claiming
  that the previous sample was preserved. A fault-injection test covers it.

The sample and collection pointer are separate writes, not a single transaction.
A process termination between them may leave a mismatched receipt. Successful
capture replay checks reject that mismatch; this review does not claim crash
atomicity or hosted verification. A live scheduled run remains pending release.

The release paths now run `python -m scripts.verify_prior_matchup` before Git
publication or a direct deployment request. The verifier checks accepted archive
bytes, the collection receipt, its manifest digest, and exact numerical replay.
On a failed refresh, it requires an archived successful receipt for the preserved
sample. A newly written sample without that receipt is rejected. This detects
the interrupted-write mismatch without claiming the writes are transactional.

The real accepted artifact passed verification. A fault test covers normal
success, preserved fallback, an unreceipted replacement, receipt mismatch and
changed replay output. All 33 publication tests passed, including a test proving
that verifier failure prevents a direct deployment request. No deployment was
attempted.
