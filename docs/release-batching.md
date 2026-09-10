# Release batching

Continue development and research on `internal-development`. Its committed Vercel configuration disables automatic Git deployments for exactly that branch. GitHub verification still runs on pushes. Other branches, including `main`, retain Vercel's default deployment behavior.

Consolidate validated changes into deliberate production releases. Before merging, fetch main and reconcile automated data publications; never overwrite newer source data or publication receipts with an older development snapshot. Run the relevant checks against the reconciled result, then publish through the existing native Git flow and verify the deployed edition. Research-only work can remain on the development branch until the next release.

Do not use an Ignored Build Step to conserve deployment-rate capacity: Vercel documents that its canceled builds still count toward deployment and concurrent-build limits. Do not repeatedly retry a rate-limited release or infer that a Git push means publication succeeded.

The rate limit observed in refresh run 34526122759 remains unresolved. This configuration prevents future development-triggered deployments; it does not restore consumed capacity, establish an exact reset time, or certify a new production edition. Scheduled production refresh and odds collection remain configured independently on main.

Sources: [Git deployment controls](https://vercel.com/docs/project-configuration/git-configuration), [monorepo build skipping and limits](https://vercel.com/docs/monorepos).
