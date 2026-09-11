# Git edition byte identity — September 11, 2026

A regression using a real temporary Git repository confirmed that the staging
guard accepted a CRLF edition while Git staged LF bytes. Ordinary source text
can tolerate that conversion; an edition SHA and its retained explanation
binding cannot.

The guard now compares the actual staged blob with the working bytes for
`data/site.json` and `data/total-explanations.json`, after the existing filtered
content checks. A mismatch prevents commit/push and asks for evidence retained
from Git-identical bytes. It does not modify evidence after hashing or alter the
frozen numerical engine.

The new test failed before the fix and passed afterward. Six real-Git staging
tests and fifteen publication-orchestration tests passed. All 140 files in the
current release pass the stricter guard. This is a prepublication safeguard,
not evidence of a public deployment.

The refresh entry point now runs the frozen engine through
`scripts/refresh_edition.py`, then atomically normalizes edition line endings
before input/archive retention. Parsed JSON values must remain identical. A
failed engine run does not trigger normalization of the previous edition.
The wrapper does not rewrite the prediction ledger or change engine code.

Two wrapper tests and six staging tests pass. An isolated offline refresh using
retained real inputs produced 272 games, preserved selected predictions and
ledger bytes, and matched the actual staged Git blob. Its report is
`reviews/edition-normalization-offline.json`; that isolated output is not a new
public edition. Existing weather history separately normalizes repository JSON
fingerprints and preserves raw upstream response hashes: its four tests and
replay of 137 retained observations also pass.
