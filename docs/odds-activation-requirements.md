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

The single-attempt reader now validates immutable evidence chains and distinguishes
missing, reserved, requested and terminal evidence. See
`reviews/odds-journal-reader.md`. It does not establish complete historical coverage;
the authoritative history reader and migration rule remain activation requirements.

The development branch's ordinary `collectOdds()` entry point now supplies the
immutable journal to the existing collector. That stages recording of reserved,
requested and terminal evidence on the current schedule; it does not activate
the planned executor, change quotas, or establish older coverage. A journal
failure before dispatch prevents acquisition while preserving the reservation.
The public deployment has not yet been updated or observed using this wiring.

Then exercise the actual hosted writer with bounded acquisition, storage-failure
and retry scenarios, and verify its durable readback. Reconcile the provider's
current quota with the migration allowance. Finally connect the schedule and
observe actual scheduled runs. The prior offline cadence experiments do not
establish sufficient live capacity or guaranteed closing captures.

The current 30-minute cooldown, 155-attempt cap and 31-day window remain the
implemented policy. Any bootstrap allowance or policy change requires an explicit
documented rule and tests; it cannot be inferred from the missing history record.
