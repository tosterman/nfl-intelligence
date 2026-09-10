# Verified personnel observation history

`scripts/personnel_changes.py` verifies each archived capture's content hash, its raw CSV source hash, acquisition/source ordering and exact reproduction by the personnel normalizer. The report retains capture/source identities and normalized-code hashes. Eight retained captures contain identical source bytes and 139 rows each: seven transitions, zero observed changes.

Changes use the injury feed's player ID within season, game type, week and team. This is not a resolved cross-provider canonical player ID. Changed name/position/status/injury fields retain before/after values; new scoped rows are first-observed and disappearing rows are no-longer-present. Neither disappearance nor a blank designation means available. Observation interval endpoints are acquisition times, while event time remains explicitly unknown. The first snapshot is a baseline, not evidence that its rows appeared on that acquisition date.

Five tests cover identical redownloads, actual designation changes, unknown event time, disappearance, refusal to join new scopes/IDs and rejection of duplicate identities or nonmonotonic captures. The real archive replay passed all eight source/capture checks and reproduced zero changes.

This is an auditable foundation for change attribution. It is not yet integrated into forecast revision explanations or the public matchup interface. Source report timestamps, cross-feed identity resolution, confirmed starters and numerical personnel effects remain unfinished. Production forecasts are unchanged.
