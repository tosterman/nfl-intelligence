# Experimental policy-to-collector adapter

`runPlannedOddsCollection` connects the existing read-only collection decision to
the existing collector through injected dependencies. No route or scheduled job
invokes it, and no live provider request was made during development.

The adapter obtains history and stored feed, then evaluates the policy. Missing,
incomplete, stale or invalid history causes deferral before even the quota lookup.
If due, the existing collector checks current provider quota. The adapter then
rereads history and feed and reevaluates the decision immediately before calling
the authoritative atomic reservation. A changed decision defers without spending
a paid request. Concurrent reservations remain the store's responsibility.

The collector's ordinary thirty-minute snapshot reuse remains its default.
This adapter overrides it because the policy already checks exact-event capture:
a recent feed for another event cannot suppress a due collection. The existing
thirty-minute acquisition cooldown and 155-attempt rolling cap remain in place.

Seven adapter tests pass: incomplete history, exact-event due behavior, changed
history after quota, concurrent callers with an atomic fixture reservation, and
timeout retention preventing immediate retry, kickoff arriving during reservation,
and isolation from mutation of the reader's history array. Existing collector tests also pass,
including quota refusal, storage retry, exact readback and reservation checks.
TypeScript checking passes. Fixtures use an in-memory provider and make no network
requests. They do not demonstrate live provider/storage scheduling reliability.

Independent AI code review found a missing post-reservation clock check. A
regression reproduced a paid closing-only request after kickoff; reevaluating
eligibility after reservation now defers it and retains the consumed attempt.
The reviewer confirmed that fix with six adapter tests. A subsequent local
regression caught shared-array mutation self-blocking; the adapter now copies
the pre-reservation history array. Final validation includes seven adapter tests.

Before activation, the production history reader must establish real completeness
without interpreting a missing reservation record as an empty account. Persistent
attempt outcomes, operational scheduling, quota migration and actual hosted
failure recovery remain unfinished. This adapter is not a completed scheduler.
