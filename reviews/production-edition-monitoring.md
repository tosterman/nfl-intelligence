# Production edition identity monitoring

The production health probe now retains allowlisted identity evidence from validated responses. It separately reports whether all five feeds satisfy freshness/structure checks and whether the public forecast edition matches the repository's intended generated time, model version and schedule source hash. Overall health requires both.

An older public generated time is `behind-intended`; a newer edition or changed identity is `different-identity`; unavailable evidence is `unverified`. Timezone-equivalent timestamps match. A concurrent publication newer than the checkout can produce a mismatch that should be rechecked against a fresh checkout. This is an identity comparison, not exact artifact verification; the existing publication-capture verifier remains required for full forecast bytes and snapshot eligibility.

On September 10 at 21:26:57 UTC, the actual public probes returned healthy freshness results for forecasts, odds, personnel, weather and quarterback context. Edition comparison failed: the public generated time was 20:09:04 while the intended repository edition was 20:24:19. Their source hashes also differ. `production-edition-health.json` retains these identities and acquisition timestamps. The process correctly returned exit code 1 despite fresh feeds.

Four new tests cover equivalent timestamps, older/newer or changed identities, missing evidence, and exclusion of unexpected payload fields. Seven existing production-health tests pass. No provider odds request or analytics event was sent. Production scheduling of this revised monitor remains pending the consolidated release.
