# Scheduled collection is not yet established

At the timestamp retained in `scheduler-observation.json`, GitHub's schedule-filtered workflow API reports zero odds-collection runs, zero forecast-refresh runs and one health-monitor run. All three workflows are active. The odds workflow exists on the repository's default branch, main, and is configured for 01:17, 06:17, 11:17, 16:17 and 21:17 UTC. The earlier successful odds executions were manually dispatched.

The 21:17 odds occurrence has not produced an observed run at this check. This does not establish the underlying cause or guarantee that no run will appear later. A forecast-refresh occurrence has not yet been observed either; its next daily opportunity must be assessed against workflow installation time rather than treating every missing historical occurrence as failure.

[GitHub documents](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) that scheduled events can be delayed under high load and queued jobs may be dropped. Run metadata inspected here does not identify an exact intended occurrence. No exact scheduling-latency estimate is claimed.

The market panel now says collection is scheduled five times daily and can be delayed or missed, while preserving the six-hour expiry and visible quote timestamps. Three market-display tests pass. No scheduler, paid collection, production forecast or deployment was triggered by this audit.

Operational acceptance still requires observed clock-triggered collection, retained collection evidence, and the downstream audit after the consolidated release is deployed. Another successful manual run would not close this gap. The health monitor shares the same scheduler, so it is not an independent availability guarantee.
