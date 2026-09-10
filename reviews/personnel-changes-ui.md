# Matchup personnel change context

Matchup pages now include a collapsed comparison inside the existing personnel expiry boundary. The section compares only the current verified snapshot with its preceding verified capture, scoped to the game's season, competition, week and two teams. A comparison with a mismatched source or acquisition timestamp is unavailable, not a zero-change result.

The generator validates retained capture/source hashes, reconstructs normalized rows, and confirms that the newest retained capture is the current public personnel snapshot before writing `data/personnel-changes.json`. The refresh workflow rebuilds the comparison after personnel acquisition; a failed rebuild does not block core forecasts. The rendering guard prevents a stale comparison from attaching to a newer snapshot. The Git publication and recovery paths include the derived file.

Player additions are first observations in the file, not injury onset dates. Their recorded fields appear inline. Disappearing rows do not imply clearance. Changed entries show before/after values, with blank fields labeled unreported. This context does not change the numerical forecast or establish canonical cross-feed player identity.

## Evidence — September 10, 2026

The eight retained captures contain seven transitions with no observed changes; the current view therefore reports no differences. Twenty personnel Python tests, three new selection tests and nine Git publication tests pass. Local browser checks on the Chicago–Carolina matchup returned 200 in Chromium and WebKit at 320px with document width 320 and no page errors. The expanded real-data empty state was visually inspected; synthetic changed-row rendering has not been claimed as a browser pass.

UX review requested inline reported fields for newly observed players, which was implemented. The change remains staged pending consolidated production rollout. `personnel-changes-browser.json` retains the two browser observations.

Code review found no blocker in the active Git publication path. It identified missing runtime JSON files in the older REST deployment helper; its explicit allowlist now includes personnel, quarterback and venue dependencies. A packaging test checks all current source JSON imports and excludes private archives, environment files and the forecast ledger. All 87 application tests and TypeScript checking pass.
