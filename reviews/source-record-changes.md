# Source record comparison

The offline comparator verifies both source digests before comparing CSV records
by explicit keys: schedule game ID or efficiency game ID plus team. It rejects
missing/duplicate identities, malformed rows and incompatible column sets. Row
or column ordering alone can change file bytes without changing source records.
Values remain exact strings; no numeric normalization hides source differences.

`python scripts/audit_source_record_changes.py` verifies the current edition's
18 input files and the fixed retained edition through their respective manifests.
These are currently the same edition, generated 2026-09-10 23:29:01 UTC: zero
record differences. That is an identity check, not evidence of two independent
refreshes.

The audit also compares the older exact schedule preserved for joint-score
experiments with the current schedule. Both compressed and decompressed source
identities are verified. There are no added or removed games and 19 revised
game records. Changed fields are moneylines (17 games per side), spread prices
(6 per side), over/under prices (8 each), spread line (5), total line (7), and
away quarterback ID/name (one game, 2026_02_SEA_ARI). Counts overlap within games.
The complete before/after fields are retained in `source-record-changes.json`.

The older schedule's original acquisition time is not preserved. Its differences
cannot establish when a correction happened, what was known before kickoff, or
that the changed fields influenced the forecast. Source betting-line changes
are not qualified live quotes or closing-line evidence. Neither schedule input
nor any model file was modified during the audit.

Three targeted tests cover added/removed/revised rows, byte-only reorderings,
duplicate and missing identities, malformed row lengths, duplicate columns,
incompatible schemas and invalid source hashes. The next integration needs to
retain successive refresh inputs and attach verified record comparisons to
forecast revisions without claiming numerical causality from file changes alone.

All 274 Python tests passed after this addition. The offline audit completed
against the exact retained files with no source acquisition.

Independent AI review found no material defect, passed the three tests and six
malformed-input subtests, and independently reproduced the 18-file identity
comparison and 19 historical schedule revisions.
