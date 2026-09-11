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

The scope engine and a retained-source rehearsal are now implemented in
`scripts/season_usage.py` and `scripts/audit_season_usage.py`. Five focused tests
pass, alongside the five existing historical-usage tests. The actual retained
source produces no eligible current-season appearances for all 139 Week 1
reports, as required: the first two games cannot enter those earlier weekly
contexts. `season-usage-rehearsal.json` retains that negative result.

`refresh_participation.py` now acquires and retains season-specific raw CSV and
source metadata, with a separate collection outcome. Live acquisition returned
the same verified 187 rows. Two collector tests cover malformed/empty/wrong-season
data, duplicate identities and invalid shares, including preservation of prior
source bytes on failure. Six scope tests now include named postseason rounds.

`build_season_participation.py` now binds the exact current personnel and QB
inputs to the identity audit, validates retained source and registry bytes, and
uses the earliest of weekly kickoff, report acquisition and participation
acquisition as the cutoff. The initial artifact has 139 reports: 134 matched
identities and five withheld. A real-source binding test verifies the empty
Week 1 sample, withheld identities, failure/retained-source labeling and rejection
of an audit for different personnel inputs. Duplicate/blank CSV headers now fail
validation following independent review. Team partitions use the same overall
eight-appearance sample.

The local public selector/UI now presents current-season evidence above the
separate prior-season history inside the participation disclosure. Three selector
tests cover exact report identity, sample/team counts, missing records, retained
dates, malformed counts and timing guards. All 188 application tests passed;
the build generated 319 pages and 26 publishing/packaging tests passed.

Four Chromium/WebKit cases at 320 and 1280px verified keyboard disclosure,
separate season headings, the actual empty Week 1 sample, no page overflow and
zero scoped axe violations. An initial browser driver stalled during cleanup
after its browser exited; the rerun saved each case separately and completed all
cases and cleanup. The mobile screenshot was inspected. Audience source review
requested explicit weighting/sample-limit wording for future nonempty samples;
that text now appears directly beneath the current-season figures.

The refresh workflow now collects and binds participation after identity audit,
retains recovery inputs, and stages the new public artifact for native release.
The direct-release file list includes it. This wiring is not an observed scheduled
run: the publisher remains paused and the new UI has not been publicly deployed.
Positive current-season browser behavior and a real weekly rollover still need
verification. The feature does not change numerical forecasts, claim player
quality or infer expected availability from observed participation.
