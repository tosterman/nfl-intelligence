# Integrated verification checkpoint

Source commit: `d7d3ab5a890b66328f063d635362801b9d46f00e` on `internal-development`.

Local verification on September 10, 2026 completed successfully:

- `python -m unittest discover -s tests -p 'test_*.py'`: 222 tests, 30.496 seconds, no failures.
- `npm test`: 97 tests, no failures or skips.
- `npm run typecheck`: exit zero.

The CLI rejection and personnel/quarterback acquisition-failure messages in Python output are exercised negative paths; the suite reports OK. These tests cover model and evidence invariants, acquisition failure behavior, input identity, publication recovery, and application components. They do not demonstrate prospective model accuracy or commercial readiness.

GitHub run [34536655502](https://github.com/tosterman/nfl-intelligence/actions/runs/34536655502) completed successfully for the preceding source commit `36f33e5781ac53c52bb495af21bac845b28e8ab0`. At this checkpoint, PR 1 is an open draft at `d7d3ab5` and its status-check rollup is empty. That is missing current-head hosted evidence, not a failed build or permission to reuse the preceding commit's result as current.

No production push, forecast regeneration or provider collection was performed for this checkpoint. Input-cache mismatch and hosted recovery verification remain as documented in `recovery-input-retention.md`; Vercel publication remains pending capacity recovery.
