# Read-only collection decision layer

`src/lib/odds-collection-decision.ts` makes a bounded collection proposal without network access or writes. It keeps the existing store's thirty-minute cooldown and 155-attempt rolling limit. The alternate fifteen-minute cadence remains a separate experiment.

The caller must supply proven-complete acquisition history observed within the preceding minute. Missing or explicitly incomplete history blocks a proposal instead of being interpreted as zero usage. Attempts must be strictly increasing and cannot postdate their observation. This API does not itself establish completeness; the missing live reservation record cannot be promoted into a complete empty history.

A regular refresh becomes due after 5.5 hours. During the final ten minutes before kickoff, an exact home/away/kickoff event captured in the final fifteen minutes suppresses repeated acquisition. A recent capture of another event does not. Capturing an event with missing or stale bookmaker prices is not a qualifying close: that remains the separate market audit's job. Cooldown and budget restrictions still apply to due requests, and returned retry times require reassessment rather than promising a closing capture.

Five decision tests and all 122 application tests passed, with TypeScript checking. A regression first reproduced acceptance of an attempt timestamp later than the history observation; the decision now rejects that chronology. Independent review found no material blocker for the stated experimental scope.

No route or workflow calls this module. Before wiring it to production, the caller must obtain trustworthy history, perform the authoritative atomic reservation, reconcile snapshot reuse and provider quota, and implement bounded retries. This module is not a completed scheduler or a guarantee of request availability.
