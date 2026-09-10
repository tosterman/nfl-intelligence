# Automated market audit retention

The audit workflow checks out trusted `main` after every completed **Collect and verify odds** run, including failures, or on manual dispatch. It exports already retained odds, evaluates checkpoint coverage, bundles the report and exact allowlisted inputs, then uploads the bundle to create-only private Blob storage. An uncached byte-for-byte readback is required before a successful receipt is written. No provider odds acquisition occurs here.

A sanitized run outcome is retained on success or failure as a 90-day GitHub artifact, together with the compact storage receipt when retention succeeds. The private bundle contains the report, source data, selection code, frozen protocol, and export manifest. Original capture files remain at the private Blob paths in that manifest; they must remain retained and hash-verified for replay. The protocol publication receipt is embedded in `report.json`. Replay uses that report's `checkedAt` and `coverageThrough`; rerunning today's CLI is a new audit, not a replay.

## Verified September 10, 2026

- Local end-to-end run stored and read back the 229,206-byte bundle identified by `reviews/market-audit-retention.json`.
- Repeating retention of the same bundle preserved its original storage upload timestamp and verified identical bytes.
- All 11 bundled files passed their recorded SHA-256 hashes. Replaying from bundled forecast inputs and the matching verified export reproduced all 544 checkpoint records exactly.
- 21 market tests and TypeScript checking passed. Independent review found no release blocker in this bounded integration.
- The repository's `BLOB_READ_WRITE_TOKEN` Actions secret was configured and its presence verified without exposing its value. It is injected only into the audit step.

The workflow has not run on GitHub yet: the implementation remains on `internal-development` pending the consolidated release. Local success is not hosted scheduling evidence. The receipt is storage evidence, not evidence of a profitable forecasting edge. There are currently 3 pre-protocol exclusions and 541 pending checkpoints, and no matched markets.

## Operation

Run `python scripts/run_market_audit.py` from the repository with `BLOB_READ_WRITE_TOKEN` available to the process. It requires the installed Node dependencies and Python requirements. Failures return nonzero and cannot produce a new verified receipt. Keep original private odds archives: deleting them would break reproducibility. The current exporter downloads the retained history for each run; its bounded runtime and bundle-size guards fail explicitly as history grows, so incremental export will be needed before large-scale operation.

A founding-priority review caught the success-only trigger gap. The workflow now also audits failed/cancelled completed collections, so missing checkpoint evidence can still be assessed. The runner writes stage and timestamps in a finally block and removes an old storage receipt before starting. Export/report failure tests confirm no exception text or secret-like subprocess output enters the retained outcome. A fresh local end-to-end run verified successful private retention with the new run outcome. Hosted execution remains pending.

Independent review passed the failure-handling change. Abrupt process termination or setup failure before Python starts cannot guarantee a finally-written record; a missing artifact fails the upload rather than reporting successful retention.
