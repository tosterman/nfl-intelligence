# Forecast context integrity

A regression reproduced a rescheduled-game eligibility defect: a valid forecast receipt could qualify against a different kickoff because the snapshot hash covered only game ID, not the original matchup context.

New production snapshots include season, week, game type, home/away assignment, kickoff, venue and neutral-site status in their hashed payload. Deduplication requires matching context even when predicted scores are unchanged. Prospective grading and current-snapshot selection require the same recorded context, with equivalent timezone representations accepted. Missing or changed context fails eligibility.

Existing ledger entries and receipts are not rewritten. Legacy snapshots without recorded context remain visible in revision history, but do not qualify for the stricter prospective record. The history panel is independent of current-forecast availability; entries use recorded team identities or explicitly unknown legacy labels. Numerical revision comparisons are suppressed when context is missing or different.

Verification: all 180 Python tests pass, including the reproduced reschedule case and rejection of missing context, different teams, season/week/type, venue and neutral-site status. TypeScript checks and revision tests pass. Browser inspection confirms the local legacy-history labels, suppressed comparisons and 390-pixel layout. Independent review confirmed the grading/deduplication guards and identified the history-display issue subsequently corrected.

The frozen joint-score reference still validates: it pins the numerical evaluator, solver and baseline implementation; publication-code identity is recorded separately and is not a reference-enforced hash. No frozen research reference or archive was altered.

Release requirement: run a successful forecast generation and verified publication after deployment before claiming newly context-qualified forecasts. Current data files were not regenerated in this change. Previously reported publication-only eligibility must not be conflated with this stricter context-qualified record. The separately archived joint shadow records already contain matchup context and retain their own verification rules. Prospective quote matching remains unfinished.
