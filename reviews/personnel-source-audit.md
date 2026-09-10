# Personnel source feasibility — September 10, 2026

The current nflverse release contradicts the older availability documentation: actual 2025 and 2026 injury CSV assets exist. The [availability page](https://nflreadr.nflverse.com/articles/nflverse_data_schedule.html) still describes the prior outage. Treat that paragraph as outdated for file availability, not as a reason to abandon personnel integration.

`python scripts/audit_personnel.py` acquired the current season file, checked exact URL, length and SHA-256 against GitHub release metadata, and inspected coverage. Its aggregate evidence is retained in `personnel-source-audit.json`; downloaded individual records remain in ignored `release-recovery/personnel/` during evaluation. This is a research audit, not a production freshness validator.

Verified snapshot: 139 rows, Week 1, 30 teams, no missing player IDs or duplicate player/week keys. Denver and Kansas City have no rows. There are 131 blank game-status designations, five Out and three Questionable; practice categories contain 25 did-not-participate, 64 limited and 50 full participation entries. These are counts in the acquired file, not a claim of complete league injury coverage.

The live schema has no `date_modified`, although the [dictionary](https://nflreadr.nflverse.com/articles/dictionary_injuries.html) documents it. Asset update time and our acquisition time are available; neither establishes the individual report time or when a practice happened. The [producer script](https://github.com/nflverse/nflverse-rosters/blob/main/exec/update-injuries.R) calls `nflapi::nflapi_injuries` and publishes its output. The data repository declares [CC BY 4.0](https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md); retain attribution, the license link and transformation notes in any public presentation. This does not grant NFL branding or claim official endorsement.

## Integration decision

Proceed with an explicitly sourced practice/report snapshot module before attempting player-value adjustments. Match season, game type, week and team; preserve raw bytes and collection time. Render blank designations as unreported and missing team coverage as unknown. Keep practice participation distinct from game status. Do not say a player is healthy because absent from this file or infer a confirmed starter from a depth-chart rank. Do not attach this newly acquired snapshot to the completed Seattle opener as pregame evidence.

Use a separate first-observed archive for subsequent snapshots. Changes can then mean first observed by this project, not the precise time the team issued an update. Obtain or corroborate per-report dates before calling these current dated injury reports. A numerical personnel model additionally needs starter identification, snap-weighted player value, historical availability vintages and prospective validation. None of those requirements is satisfied merely by this file's existence.

Next concrete work is a normalized snapshot contract with source-age and coverage states, acquisition archives and team/week matching tests, then a matchup context panel. The current production model remains unchanged while those requirements are implemented.
