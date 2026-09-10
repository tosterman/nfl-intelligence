# Retained odds collection evidence

The odds workflow now uploads `odds-collection-report.json` after success or failure, retained for 90 days under a run-ID and attempt-specific artifact name. The report records start/completion times, success, execution stage, HTTP status and a validated result. New acquisitions include snapshot time, hash, event count and reported remaining credits. Snapshot reuse is explicitly distinct and does not invent a new hash or quota observation.

Only allowlisted fields enter the report. Raw provider/endpoint bodies, credentials, authenticated URLs and exception messages are excluded. A missing configuration test executed the actual script, exited 1 and retained a configuration-stage failure report without a network request. Parser tests reject unsupported statuses, missing capture identity, invalid quota, and stale/future acquisition timestamps. All 78 application tests and TypeScript checks pass.

The API currently returns a generic error on collection failure, so a failed report cannot distinguish reservation denial, provider rejection and storage failure inside that endpoint. It records the observed stage and HTTP status without inventing a deeper cause. Process termination before finalization can prevent report creation; the artifact step then fails visibly on the missing file. Hosted artifact verification for this change remains pending release/workflow execution. No extra paid acquisition was dispatched merely to test reporting.

Scheduler audit at 20:40 UTC on September 10 found only the previously verified scheduled health run. The 21:17 UTC odds slot had not occurred; this audit provides no evidence of a missed odds job.
