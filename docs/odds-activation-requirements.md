# Planned collector activation requirements

The policy-to-collector adapter is implemented and tested locally. It does not
replace the current production collector or schedule. The latest read-only
observation, 2026-09-11 13:33 UTC, found no live reservation record.

Before activation, establish one authoritative acquisition writer and document
how existing request usage is carried into its budget. Do not create fabricated
attempt timestamps or label an empty new record as complete history. A successful
quote archive proves a response was retained; it does not enumerate failures or
requests whose storage response was lost.

The production history reader must distinguish unavailable, incomplete and
complete coverage. New attempt records must be persisted before provider access,
and remain consumed after provider timeout or uncertain storage completion. The
existing atomic reservation is still responsible for concurrent writers and the
rolling attempt cap. Persist outcome evidence so failures can be audited, without
putting credentials or raw request URLs in the journal.

Then exercise the actual hosted writer with bounded acquisition, storage-failure
and retry scenarios, and verify its durable readback. Reconcile the provider's
current quota with the migration allowance. Finally connect the schedule and
observe actual scheduled runs. The prior offline cadence experiments do not
establish sufficient live capacity or guaranteed closing captures.

The current 30-minute cooldown, 155-attempt cap and 31-day window remain the
implemented policy. Any bootstrap allowance or policy change requires an explicit
documented rule and tests; it cannot be inferred from the missing history record.
