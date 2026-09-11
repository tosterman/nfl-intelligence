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

Windows refresh output should be normalized before input/archive retention.
The current edition already uses LF bytes. Automating that normalization in the
refresh entry point remains a follow-up; a future mismatch now fails explicitly.
