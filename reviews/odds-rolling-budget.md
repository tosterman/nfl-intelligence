# Rolling odds acquisition budget

The shared acquisition reservation now retains a schema-2 history of at most 155 attempts in a rolling 31-day window. Each reservation is committed with the same conditional storage write that prevents overlapping collectors. A rejected write cannot authorize a provider request. The live quota preflight still rejects unknown or insufficient account credits before reservation.

For the current three-market, one-region endpoint, 155 reservations represent at most 465 reserved credits. This is a reservation budget, not a claim that the provider billed exactly that amount in an identical wall-clock interval: requests occur after reservation, failures can be uncharged, and provider quota resets are not assumed. The request cost follows [The Odds API v4 documentation](https://the-odds-api.com/liveapi/guides/v4/), checked September 10, 2026.

A failed or timed-out operation never refunds its reservation. Capacity becomes available only when its timestamp leaves the rolling window. Manual captures consume the same allowance as scheduled captures, so extra manual requests can eventually displace scheduled requests. Collection then fails explicitly; the UI's existing stale-data handling applies.

Migration from schema 1 preserves its single known attempt. It cannot reconstruct earlier attempts and must not imply historical budget coverage. The guard applies only to cooperating deployments using this state; the currently deployed older collector and other users of the API key are outside that scope. Rolling storage history is not an immutable billing ledger. A future increase in requested markets or regions requires updating and revalidating this budget.

## Verification

84 application tests and TypeScript checking pass. New tests fill the budget and race eight collectors for its last slot, reject the next attempt, reopen only expired capacity, preserve the known legacy attempt, and fail closed for corrupt or inconsistent history. An integration test confirms an exhausted budget prevents paid acquisition even when the provider reports available credits. Independent review found no implementation blocker and required the reservation-versus-charge distinction above. No paid provider request was made to test this change.

This change is staged on `internal-development`; production enforcement requires the consolidated release. Existing private-storage conditional-write behavior was previously verified against actual Blob storage; the new history logic was tested with the same version-conflict contract.
