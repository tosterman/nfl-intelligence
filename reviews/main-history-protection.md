# Main publication history protection

GitHub ruleset [22825308](https://github.com/tosterman/nfl-intelligence/rules/22825308), **Preserve main publication history**, is active for exactly `refs/heads/main`, with no exclusions or bypass actors. The effective branch-rules API returns `deletion` and `non_fast_forward`. Its reviewable request configuration is in `docs/main-history-ruleset.json`.

These rules block main deletion and non-fast-forward updates while allowing ordinary authorized commits. The publishing workflow uses ordinary pushes and rebases on concurrent changes; it never force-pushes. Normal push of commit `868f16f` succeeded after activation. No destructive force-push or deletion was attempted as a test; enforcement evidence is the active and effective GitHub rules configuration.

This is limited history protection, not complete change control. Required checks, required reviews, contributor restrictions and an explicit policy for the automation writer remain unresolved. Repository administrators can change the ruleset, so retained Git history is not an immutable third-party notarization.

## Publisher verification and separate hosting failure

[Refresh 34526122759](https://github.com/tosterman/nfl-intelligence/actions/runs/34526122759) passed acquisition, application/Python tests and build, then successfully pushed `21e8dc313bd788877b0700f97abc273faceb3b11` under the active rules. Publication stopped when Vercel returned failure with `https://vercel.com/khnum?upgradeToPro=build-rate-limit`. This is a hosting build limit, not a rejected branch write. The recovery artifact was downloaded to `release-recovery/build-limit-34526122759`; no successful receipt was accepted and the final receipt-commit step was skipped.

The live status endpoint remained HTTP 200 with the prior verified edition generated at `2026-09-10T20:09:04.084122Z`. Git main therefore contains a newer unverified edition than the public deployment. The local classifier now recognizes the trusted Vercel rate-limit failure; nine publication tests pass, including rejection of the same URL if presented as a successful deployment or by an untrusted author. This fix is committed locally pending a deployment-capacity recovery plan. No paid hosting upgrade or blind deployment retry was performed.
