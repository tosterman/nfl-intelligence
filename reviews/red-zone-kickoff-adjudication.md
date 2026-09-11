# Nullified kickoff adjudication

The [official Bengals–Vikings gamebook](https://static.www.nfl.com/image/upload/v1758541357/gamecenter/f665f7cb-311e-11f0-b670-ae1250fadad1.pdf),
PDF pages 15–16, corroborates the source description: offsetting penalties
nullified the late-third-quarter kickoff, and a replacement kickoff produced a
touchback before Cincinnati's next possession. No full gamebook is republished.

`data/red-zone-adjudications.json` documents the sole exception, Cincinnati at
Minnesota 2025 Week 3, play 3284. It excludes that nullified kickoff only for the
pinned full-source SHA-256 and exact parsed-row SHA-256. The original archive is
unchanged. The application rejects a changed source, modified/missing/duplicate
record, unsupported action or non-kickoff record. It does not assign unknown
scoring flags a default zero.

CSV parsing preserves embedded source newlines through `StringIO`; an initial
row hash made through newline-translating text IO correctly failed the guard.
The retained-row regression exercises the same byte-preserving parser as the
audit, including the full archive digest check.

Re-running `python scripts/audit_red_zone_phases.py` now accepts all 6,046 groups:
1,824 inside-20 groups, 4,222 outside, no ambiguous owners, no provider-indicator
disagreements and one documented adjudication. This supersedes the unresolved
kickoff finding in `red-zone-phase-reconciliation.md`. Internal agreement does
not establish official red-zone rates; touchdown numerators, schedule cutoffs,
coverage, exact boundary conventions and UI remain to be completed.
