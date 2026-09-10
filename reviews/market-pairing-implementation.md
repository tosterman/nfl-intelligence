# Market pairing implementation status

The v1 policy was committed at `a81fc7fa2dabc94651b20be7aa9339e78c63dc68` and retrieved byte-for-byte from its immutable GitHub URL at 20:53:33 UTC on September 10, before the specified September 11 00:00 UTC activation. The publication receipt retains the content hash and observed/HTTP dates. The protocol file is frozen; subsequent policy changes require a new version.

`scripts/market_pairing.py` currently supplies checkpoint, forecast and quote selection primitives. Seven tests exercise pending/pre-protocol checkpoints, future upload rejection, missing-book handling, conflicting acquisition timestamps, strict cutoff exclusion, stale bookmaker updates, changed kickoff, forecast tampering and publication after the decision checkpoint.

The quote selector accepts already verified archive envelopes plus original storage-upload metadata. That trusted ingestion boundary is not implemented here. There is not yet a production runner, durable pairing report, closing capture mechanism, settlement convention or CLV calculation. The existing schedule cannot promise final-15-minute coverage. No real game has been reported as paired under this implementation, and no extra provider acquisition was triggered.

The forecast selector requires the context-bearing snapshots introduced by the pending release. Legacy snapshots cannot be silently backfilled into this cohort. This research evidence path remains independent of public betting recommendations and numerical model promotion.
