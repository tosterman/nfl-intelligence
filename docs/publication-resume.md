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
