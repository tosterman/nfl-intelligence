# Season-aware participation — feasibility and implementation scope

Independent founding review identified a remaining section 11 gap: the usage
pipeline is fixed to 2025. `audit_player_usage.py` pins a 2025 source, and
`player-usage.ts` rejects the current season. Existing evidence remains valid
historical context but cannot show emerging current-season roles.

A September 11 16:29 UTC source acquisition returned 187 rows for the first two
2026 games. Retained bytes and acquisition metadata are in
`player-usage-2026-source.csv.gz` and `player-usage-2026-feasibility.json`.
Registry joins identify 22 candidate reported players, not 22 accepted identity
matches or valid pregame samples. All current personnel reports have week 1
scope: these same-week appearances must be excluded from their weekly context.

Implementation requirements:

1. Acquire season-specific sources atomically, retaining exact bytes, retrieval
   times and collection status. Keep the accepted 2025 fixture reproducible.
2. Derive a weekly context cutoff from the actual schedule. Filter appearances
   to earlier weekly scope and retain the existing completed-game/24-hour
   embargo. Future and same-week observations cannot alter earlier contexts.
3. Require corroborated player identifiers; preserve current-team and former-team
   appearances separately. Do not infer absence or zero snaps from missing rows.
4. Produce separate current-season and previous-season evidence, each with its
   sample count, last appearance and source provenance. Provider failures retain
   explicitly dated evidence; they do not relabel historical data as current.
5. Extend public selectors and personnel disclosure only after source replay and
   scope tests pass. Verify rollover, transfers, duplicate identities, empty
   current-season samples, failed collection and mobile display.

This work is not implemented yet. It must not change the numerical forecasts,
claim player quality or infer expected availability from observed participation.
