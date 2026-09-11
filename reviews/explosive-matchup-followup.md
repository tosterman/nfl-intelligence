# Count and release follow-up

Corrected the UI's inaccurate "Games count equally" sentence: the implementation
pools eligible plays. Each eligible play counts equally; it does not average
game-level percentages. Forecast numbers and historical counts did not change.

Three component checks now include a fixed San Francisco/Los Angeles sample,
asserting all eight percentages and denominators in offense/defense column order.
The wording regression failed before the correction and passed afterward.

`python scripts/check_explosive_matchups.py` verified 15 forecast-bearing matchups
in Chromium and WebKit at 320px: 30 browser/game combinations, 240 displayed
percentages and denominators matching the retained artifact, no document overflow
and no page errors. Detailed output is `explosive-matchup-count-audit.json`.

GitHub run 34602545248 failed the release-file coverage check. Local reproduction
confirmed `data/explosive-plays.json` was absent from the explicit REST deployment
allowlist. Added that runtime artifact; the release-file test now passes while
continuing to exclude raw source archives. No deployment was attempted.
