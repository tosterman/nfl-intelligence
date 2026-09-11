# Participation replay across Git checkouts

An isolated replay from Git files found that all 139 participation records
matched, but the identity-audit input fingerprint differed after Git converted
Windows CRLF line endings to LF. The builder now fingerprints that generated
repository JSON using LF. Raw schedule, personnel and upstream source hashes
remain unchanged.

The regression failed before the correction and passed afterward. The current
artifact was rebuilt at its original calculation time: only the identity
fingerprint changed. A second isolated replay using staged Git files and the
original schedule bytes matched the entire artifact, including all 139 records
and metadata. The schedule is an ignored acquisition input, so this check
explicitly supplied it; Git alone does not contain every replay input.

This verifies local reproducibility, not a scheduled run or public deployment.
