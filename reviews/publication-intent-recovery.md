# Retain publication intent before remote push

The publisher previously created `release-recovery/git-publication.json` only after a successful Git push. A rejected push therefore left the uploaded recovery bundle without its intended commit identity. A new isolated failure test reproduced the missing file before the change.

The publisher now writes that identity atomically after the local commit is resolved and before attempting the push. Its `evidenceType` is `publication-intent-only`: it is neither a push confirmation nor a deployment or public-capture receipt. Existing exact-public-artifact verification still controls whether `data/publications.json` receives a receipt. Concurrent remote changes still reject the push; this does not introduce retries, rebases or force pushes for the tested edition.

Verification: all twelve native publisher tests and five publication preflight tests pass. The new cases inject a rejected push and an intent-write disk failure: rejection retains the intended commit and unchanged prior receipts without calling capture; disk failure prevents the remote push. An independent source reviewer found no actionable issue in the pre-push intent change. These are isolated failure drills, not a hosted production incident or deployment verification.
