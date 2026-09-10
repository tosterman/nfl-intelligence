# NFL Intelligence implementation plan

Goal: deliver the founding document as an honest, attractive, tested production publishing platform.
Architecture: deterministic offline model and append-only snapshots served by Next.js; optional external feeds fail closed.
Spec: docs/design.md. Original: founding.docx.

- [ ] Data and engine: scripts/build_data.py consumes nflverse game CSV; exports data/site.json and data/ledger.json. Fit time-decayed ridge offense/defense and evaluate walk-forward with held-out seasons. Verify target exclusion, additive contributions, score/probability consistency, and immutable snapshots.
- [ ] Domain contracts: src/lib/types.ts and src/lib/math.ts enforce market sign conventions, odds conversions, push handling, probability validation and stale quote rejection. Run node tests before and after implementation.
- [ ] Consumer experience: src/app and src/components provide slate, filters, game breakdown, ratings, methodology, performance and trust pages. Verify routing, empty states and mobile interaction.
- [ ] Production operations: security headers, social metadata, sitemap, refresh workflow, safe analytics and ad integration boundaries. Verify build and dependency audit.
- [ ] Independent reviews: craft and audience advocate/adversary passes, including skeptical fan, professional bettor, statistician, league integrity, media executive, accessibility, privacy/security and monetization. Reconcile findings into reviews/ and fix confirmed defects.
- [ ] Release: GitHub repository and CI; Vercel deployment and live verification. Document external account/feed/advertising requirements exactly.
