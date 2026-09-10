# Market pairing implementation status

The v1 policy was committed at `a81fc7fa2dabc94651b20be7aa9339e78c63dc68` and retrieved byte-for-byte from its immutable GitHub URL at 20:53:33 UTC on September 10, before the specified September 11 00:00 UTC activation. The publication receipt retains the content hash and observed/HTTP dates. The protocol file is frozen; subsequent policy changes require a new version.

`scripts/market_pairing.py` currently supplies checkpoint, forecast and quote selection primitives. Seven tests exercise pending/pre-protocol checkpoints, future upload rejection, missing-book handling, conflicting acquisition timestamps, strict cutoff exclusion, stale bookmaker updates, changed kickoff, forecast tampering and publication after the decision checkpoint.

The quote selector accepts already verified archive envelopes plus original storage-upload metadata. `export_odds_evidence.ts` now exports existing private Blob archives through authenticated, uncached reads and completes a manifest only after all listed objects are verified. `market_capture.py` checks compressed/content identity, path and acquisition agreement, storage/export chronology, and normalized price/line values. The checkpoint wrapper automatically enforces pending/pre-protocol statuses and strict closing cutoffs. Ten market tests pass; three actual exported captures, each with 239 events, pass ingestion. No paid provider request was made.

Storage timestamps are authenticated provider metadata, not third-party notarization. The private export stays in the ignored recovery directory. A local report runner now retains a content-addressed checkpoint audit with input, code, protocol, export and capture hashes. Production scheduling, remote report retention, a closing capture mechanism, settlement convention and CLV calculation remain unfinished. The existing schedule cannot promise final-15-minute coverage. No real game has been reported as paired under this implementation.

The forecast selector requires the context-bearing snapshots introduced by the pending release. Legacy snapshots cannot be silently backfilled into this cohort. This research evidence path remains independent of public betting recommendations and numerical model promotion.


## Retained report verification — September 10, 2026

`report_market_pairing.py` verifies the frozen protocol publication before loading authenticated archive exports. It emits both checkpoints for every scheduled game and records separate checkpoint and market status counts. The first current-season report covers 272 games: 3 pre-protocol exclusions and 541 pending checkpoints, with no matched comparisons. Raw quote evidence stays in the ignored recovery directory; `market-pairing-report-summary.json` retains its hash and compact coverage metadata.

Independent review found that current wall time could extend beyond the export's upload coverage. The runner now requires the verified export `startedAt` boundary and labels later due checkpoints `export-too-early`, without assessing missing quotes or forecasts. Pending and pre-protocol statuses remain explicit. Tests cover this boundary, future exports, complete checkpoint coverage, future bookmaker exclusion, duplicate games, missing kickoff, protocol tampering, per-market missingness, and deterministic forecast timestamp ties. All 18 market tests pass. The reviewer verified the correction with no remaining issue in this bounded fix.
