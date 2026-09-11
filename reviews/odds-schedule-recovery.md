# Odds freshness recovery — September 11

At approximately 17:37 UTC, local and public `/api/odds-status` both returned
503 for the snapshot acquired at 11:23:13.715 UTC, beyond its six-hour limit.
The main odds workflow was active with a 16:17 UTC schedule, but its run list
contained no execution for that slot. This establishes an absent observed run,
not the cause of the scheduler delay or omission.

Manually dispatched run 34628799978 completed successfully. It captured 212
events at 17:38:29.911 UTC with archive SHA
`321bdf0b9569193911bcad7b9deb6202cdacc12683d397101cdbcdb962259e53`.
The provider reported 461 credits remaining. Public status then returned healthy
HTTP 200 with the exact new acquisition time.

A real Chromium check of the public Atlanta–Pittsburgh page at 390px showed
nine eligible sportsbooks, timestamped spread/total/moneyline prices, and no
horizontal overflow. See `odds-recovery-browser.json`. This restores current
public odds without deploying the development branch or weakening expiry.

Automatic schedule reliability remains unproven. A manual recovery is not an
actual scheduled success; the next scheduled collection and freshness interval
still need observation. Existing cache entries on local development can lag
public invalidation by the configured fifteen-minute read-cache interval.
