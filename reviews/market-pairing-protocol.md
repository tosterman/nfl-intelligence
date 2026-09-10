# Prospective market pairing v1

This protocol begins at 2026-09-11T00:00:00Z and applies only to decision checkpoints on or after that instant. Earlier checkpoints are excluded, never backfilled into the prospective cohort. Publication of this protocol must be verified before activation; implementation alone is not preregistration evidence.

The entry checkpoint is exactly 24 hours before the recorded kickoff. Select the latest generated, hash-valid forecast whose matching game context was verified publicly available at or before that checkpoint. Publication and generation must both precede kickoff. Use each bookmaker separately, without choosing a favorable bookmaker or dropping adverse comparisons.

For each bookmaker and market, use the latest archived acquisition available by the checkpoint. Both acquisition time and storage upload time must be at or before it, and the bookmaker update must not postdate acquisition. Acquisition and bookmaker update must each be no more than six hours old. Do not fall back to an older acquisition when the newest matching event omits that bookmaker or market: record the gap.

The closing observation checkpoint is kickoff, strictly excluding captures or storage uploads at/after kickoff. Require acquisition and bookmaker update within the final 15 minutes. This is a sampled near-kickoff quote, not proof of the bookmaker's true closing price. The current five-hour acquisition schedule will leave many missing closing observations; record those gaps rather than widening the window afterward.

Event identity must match home/away assignment and kickoff exactly. A reschedule requires explicit reconciliation; it must not silently borrow another event or checkpoint. Ambiguous same-time conflicting captures fail closed. Missing forecast, quote, market, book, upload evidence or stale observation receives an explicit status. Pending future checkpoints are not failures.

Keep spread, total and moneyline separate, retain both sides' prices and source/update times, and retain forecast/odds hashes. No simulated bet, stake, ROI, profitability claim or model promotion follows from pairing alone. Later settlement/CLV metrics require a separately fixed convention and must disclose paired counts and missing coverage. Do not adjust this protocol after seeing results without a new version and prospective start.
