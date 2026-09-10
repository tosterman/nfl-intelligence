# Source freshness review — 2026-09-10

Found a real operational defect: `/api/status` and the slate checked model generation time alone. Running the model offline against old source bytes could renew generation time and hide stale data.

Both now use a shared assessment of model generation, schedule/results acquisition, and current/previous season efficiency acquisition. Historical frozen seasons need not be downloaded daily. Missing or malformed times and times more than five minutes in the future fail closed; a small clock-skew allowance avoids false failures. The exact unrounded age controls the 30-hour boundary. Endpoint responses retain model age and add named source checks, returning 503 on failure with no-store caching. Initial server rendering can show the warning; the browser rechecks once per minute.

Four regression cases cover stale inputs with fresh generation, invalid/missing/future timestamps, precise threshold behavior and missing required efficiency seasons. Independent code review found no actionable defect. This reports source acquisition freshness, not proof that upstream content is complete or current, and does not replace feed coverage validation.

Vercel recheck: CLI54.18.7 is installed but reports no existing credentials; its device login was canceled rather than left waiting unattended. The connected team still lists zero projects. Public launch remains unverified.
