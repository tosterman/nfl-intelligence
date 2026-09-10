# Performance coverage and safe entry points — 2026-09-10

The public performance page now separates 544 regular-season and 26 postseason games. All570 remain in aggregate results. The single regular-season tie stays in error metrics but is excluded from decisive winner accuracy and Brier scoring. Small playoff counts are disclosed rather than promoted as proof of better reliability.

Added the missing total-market benchmark: closing-total MAE10.096 versus model10.251, on570 matched games. Model and market comparison errors now use the same eligible subset for each market, even when spread and total coverage differ. All-game model metrics remain in the overview. Three regressions check independent market coverage/denominators, phase reconciliation, and safe legacy-script behavior. Independent review verified current totals and identified the matched-sample safeguard, which was adopted.

Removed the obsolete executable publisher from build_data.py. It still provides model helpers, but executing it now exits with instructions to use refresh.py before modifying any artifacts. The legacy path could otherwise bypass current archive and source validation; its original implementation remains in Git history. The safe entry-point regression verifies unchanged site and ledger hashes after the refused command.

Actual local browser confirmed both phase rows and their counts. At320px the document remained305px wide; the phase table stayed inside its227px scroll region. Existing forecasts were regenerated with identical numeric predictions and new code provenance; earlier snapshots remain intact. No public publication receipt was invented.
