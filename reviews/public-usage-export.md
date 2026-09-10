# Guarded historical usage export

The historical usage and personnel-identity audits have been regenerated against the current retained personnel artifact. The previous usage audit's exact personnel hash no longer matched, so it was not imported into the UI.

`scripts/build_public_usage.py` now prepares `data/player-usage.json` only when both audits bind to the exact current personnel bytes, player scopes match uniquely, and player names and identities agree. The command also verifies the current schedule and calculation-code fingerprints against the audit. It writes through the existing atomic JSON writer. Every exported record retains the historical usage evidence and source fingerprints.

Only an exact `matched` identity status exposes historical usage. Name variants and the unresolved identifier conflict receive an unavailable state, without showing inherited snap shares. This is deliberately stricter than the research usage audit: 139 public records contain 106 available histories, versus 110 in the usage-only audit. Four name variants are withheld; the identifier conflict already lacked eligible history. Other unavailable histories remain unknown rather than zero-filled.

Reproduce using the retained source archives and matching schedule:

```sh
python scripts/audit_personnel_identity.py
python scripts/audit_player_usage.py
python scripts/build_public_usage.py
```

Three focused tests cover exact input binding, duplicate or mismatched records, unknown history, and conflicting-identity suppression. This is an intermediate integration artifact. The matchup panel and scheduled refresh do not consume it yet. Before public use, add runtime binding to the current personnel source and retrieval time, date/number validation, historical-team labels, and explicit appearance-conditioned share explanations. No current lineup, injury effect, expected snaps, or player value is inferred.

Independent automated review reproduced the exact 139-record payload and all 106 available matches, and found no material blocker for this export-only checkpoint. The full Python suite passed 219 tests.
