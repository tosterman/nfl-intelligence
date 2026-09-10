# Retain forecast input bytes — September 10, 2026

The refresh recovery artifact previously included forecast outputs and source digests but omitted ignored `data/games.csv` and `data/raw/stats_team_week_*.csv`. The workflow now retains these narrow source paths, including on failure, under its existing 90-day artifact retention. It does not upload the entire raw directory, environment files or credentials.

After a successful model refresh and before publication, `verify_forecast_inputs.py` checks the schedule and every declared efficiency source against the edition's SHA-256 digests. Missing or changed bytes fail the step. Season values are bounded integers and unique; input paths are constructed locally rather than trusted from manifest URLs. The report is included in recovery artifacts. These checks establish input identity only, not numerical replay, historical vintage availability or publication.

The isolated test covers matching, changed and missing bytes, invalid season/path values and duplicate seasons. A real retained first edition from the context-builder verification (`2026-09-10T20:51:58.138285+00:00`) and its original schedule passed all eighteen input checks in a temporary directory; the report is `recovery-input-verification.json`. This is a local retained edition, not a public release receipt.

The current working cache correctly fails against the checked-in edition: the schedule hash is `b0b01f911efc41ad05259f26938091678afde4790541c9d99268843d5c08320f`, whereas that edition declares `0461a4e0cedc2d5732d5cebe9f0287a4f5cefcdf298704a0e35575ec23278d92`. All seventeen efficiency files match. No cache or forecast hashes were rewritten to manufacture a pass. A fresh successful refresh must produce a matching set before the next publication.

Hosted upload/download recovery with these new input paths remains to be verified after deployment capacity recovers. Restoring acquisition timestamps and reproducing floating-point outputs are separate from this byte-identity check.
