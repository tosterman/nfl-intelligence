# Historical player usage audit

The September 10, 2026 audit matched current personnel GSIS identifiers through the pinned player registry to exact PFR identifiers in the 2025 nflverse snap-count release. Of 139 reports, **110 have eligible historical appearances and 29 have none**. All 29 unavailable results mean no eligible appearances, not a zero snap share or proof of no football experience. For 21 available players, the reported current team is absent from their selected historical teams.

For each player, the calculation takes at most eight most recent recorded appearances in completed games, with a strict 24-hour post-kickoff embargo. It averages the source's offense, defense and special-teams shares using a 90-day half-life. This is an appearance-conditioned average, not total snaps divided by team snaps across all scheduled games. Missing appearances are never zero-filled. The half-life and eight-appearance window are descriptive choices, not empirically validated model parameters.

The artifact preserves every selected game, team, date, source share and snap count. It refuses duplicate player-game rows, ambiguous registry identities, invalid numeric shares/counts and team/opponent disagreements with the schedule. A current report designation is copied only to identify the audited input; this audit does not confirm its accuracy or freshness.

## Evidence and limits

- Source: [nflverse 2025 snap counts](https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_2025.csv), 2,401,193 uncompressed bytes, SHA-256 `80b02a6e511aa20283551cae622b29ba4d0a6f006c489a2d91591fcad33792e7`. Acquisition matched the GitHub release asset byte count and digest; release asset update was February 9, 2026, 13:39:51 UTC. Exact CSV bytes are archived in `player-usage-source.csv.gz`.
- Registry bytes and metadata are archived separately in `player-identity-source.csv.gz` and `player-registry-source.json`. Output records fingerprints of source inputs, local schedule, personnel artifact and calculation code.
- This is current revised historical data, not a preserved pregame vintage. The time embargo does not turn it into a leakage-free historical backtest source.
- Only the 2025 season is covered. Historical appearances are months old; these are not current projected roles, confirmed availability, player quality or point costs. Rookies and other missing histories remain unknown.
- Schedule and personnel inputs are fingerprinted, but exact reruns require the matching input versions plus the recorded cutoff. Re-running the command against current files uses the current clock and creates a new audit.
- Source distribution attribution: nflverse, [CC BY 4.0 license](https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md). This audit does not establish additional downstream commercial rights.

Five focused tests verify identity ambiguity, unknown history, the exact embargo boundary, invalid data, duplicate games, a hand-calculated half-life average, missing-game handling and chronological selection of the last eight appearances. No production forecasts or public player panels consume this research artifact.

Independent review reproduced all 139 usage results, verified source hashes and passed all five tests; it found no material defect within this descriptive audit's scope.
