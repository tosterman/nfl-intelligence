# Resume the temporarily paused forecast publisher

On September 10, 2026, `refresh.yml` was disabled through GitHub Actions. Readback confirmed `disabled_manually`. The main branch still lacked the staged cooldown guard and its next nominal 10:30 UTC run would precede the provider's September 11 20:25:03 UTC retry boundary. Odds collection and health monitoring remain active. This pause prevents automated forecast publication; it does not keep the existing public forecast edition current.

Before resuming:

1. Recheck the authenticated main-commit Vercel status and retry boundary. Do not assume that elapsed time guarantees capacity. Preserve any newer provider instruction.
2. Finish the reviewed release onto main, including the cooldown guard, forecast input retention and odds collection budget safeguards. Reconcile any main-branch changes. Do not deploy the synthetic context-builder fixture.
3. Generate a fresh edition from retained real inputs, validate its pregame contexts and hashes, run the required checks, and retain publication intent. Run `python scripts/replay_forecast.py --new-snapshots` against those inputs; require zero mismatched or unreplayable new snapshots, and retain the report. Older retained revisions are reported separately rather than counted as replayed. The existing checked-in legacy edition is not an acceptable substitute for this refresh. Native publication now also requires every release file to match Git's staged contents, including removal of obsolete files; an unstaged edit or omitted generated artifact stops publication before commit/push. Keep the checkout stable while these checks run.
4. After the provider allows an attempt, complete one controlled publication, verify the exact public artifact against the expected edition and canonical ledger, and retain the publication receipt. A green build alone does not establish publication.
5. Re-enable the workflow with `gh workflow enable refresh.yml` and read back `active`. Its checkout must contain the release safeguards before it is allowed to publish. If the workflow itself is needed for the controlled publication, enable it only after those safeguards reach main and the retry boundary has been rechecked; dispatch it once and inspect that run.
6. Observe a subsequent actual scheduled run through refresh, public capture and receipt archival. A manual dispatch is not evidence of scheduler reliability. Confirm odds and health workflows remain active, and monitor feed freshness and whether the public edition matches the intended release.

Record the resumed workflow state and successful publication evidence alongside the pause receipt in `reviews/publication-workflow-pause.json`. Until then, report the publisher as paused, not operational or sustainably scheduled. No hosting upgrade or deployment retry was made as part of the pause.

For a manual edition refresh, rebuild schedule-dependent participation with
`python scripts/build_season_participation.py` after acquiring and retaining the
new schedule, as the hosted refresh workflow already does. Run the full Python
suite as well as application checks before accepting the candidate. A fresh
schedule can change only market or source-label fields while leaving predictions
unchanged; the derived participation artifact still must bind to its exact new
source hash. The September 11 candidate exposed this omission in hosted
personnel-presentation tests; do not waive that binding check.

September 11 pre-rollout observation: scheduled health run 34623950366 failed
because the older public Washington–Philadelphia weather issue passed its
30-hour limit. Direct readback confirms public weather status 503 with six of
seven eligible games available; the local release reports 200 with fourteen of
fourteen eligible games available. See
`reviews/weather-public-expiry-observation.json`. Keep freshness limits intact.
Regenerate any inputs that expire before rollout, then verify public weather
health and every other deployed feed after publication. A locally healthy
artifact does not resolve the public incident.

Independent weather rollout: deploy the runtime reader before setting the
repository variable `WEATHER_RUNTIME_ENABLED=true`. Verify that public
`/api/weather-status` reports the exact stored manifest and healthy current
coverage. Then enable the variable and dispatch `weather.yml` once; inspect its
restore, collection, source replay, storage publication, and public readback
evidence. Observe a later actual scheduled run separately. Keep the variable
unset if public verification fails. This weather workflow does not regenerate
numerical forecasts or replace the forecast publication receipt procedure above.

Independent personnel rollout: deploy the runtime reader before setting
`PERSONNEL_RUNTIME_ENABLED=true`. Run
`python scripts/verify_personnel_publication.py --url https://nfl-intelligence-one.vercel.app`
against the intended `reviews/personnel-incremental-publication.json` receipt.
Require all three public personnel, quarterback and participation endpoints to
select that exact publication and return healthy HTTP 200. Then enable the
variable and dispatch `personnel.yml` once. Inspect its real restore, collection,
replay, conditional publication and public readback, and retain its workflow
artifact. Observe a later clock-triggered run separately. Keep the variable
unset if the initial reader check fails; neither local readback nor an enabled
workflow proves public feed health. Do not regenerate or substitute timestamps
to make an expired collection pass.

Market benchmark rollout: the forecast workflow now has a nonfatal benchmark
refresh gated by `MARKET_BENCHMARK_ENABLED=true`. Keep it unset until the local
combined export/replay/private-retention run and the deployed performance page's
exact report fingerprint have been checked. The reader is a dated static audit,
so later captures do not enter automatically until a successful refresh and
deployment. Verify the gated step on a controlled forecast run, then separately
observe scheduled execution. A failed benchmark refresh preserves its prior
reader summary and cannot waive the forecast edition's publication checks.

Run `python scripts/check_market_benchmark_ui.py --origin https://nfl-intelligence-one.vercel.app --output reviews/market-benchmark-public-browser.json`
from the stable intended release checkout. This opens the actual performance
page in Chromium and WebKit, checks the report fingerprint, rendered comparison
and exclusion counts, any paired error values, keyboard disclosures and scoped
accessibility at 320px. A failed invocation removes its old output proof rather
than leaving a stale success receipt. This verifies the rendered benchmark;
forecast publication still requires the separate exact-artifact receipt above.
