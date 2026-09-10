# NFL Intelligence implementation plan

Goal: deliver the founding document as an honest, attractive, tested production publishing platform.
Architecture: deterministic offline model and append-only snapshots served by Next.js; optional external feeds fail closed.
Spec: docs/design.md. Original: founding.docx.

- [x] Data and engine: scoring/efficiency blend, chronological replay, source/code/configuration hashes, additive contributions, probability guards and append-only forecasts. Evaluation is development evidence, not an untouched holdout.
- [x] Domain contracts: market sign conventions, odds conversions, pushes, probability validation and stale quote rejection. No live quote feed connected.
- [x] Consumer experience: slate, contextual filters, game breakdown, 32 team hubs, ratings, methodology, performance and trust pages. Desktop and 320px browser checks completed.
- [x] Production foundations: security headers, social image, sitemap, refresh workflow, consent-controlled analytics integration. Live event delivery remains unverified.
- [x] Independent architecture, code and audience reviews; simulated statistical, bettor, league, media, fan, accessibility and privacy perspectives. Confirmed defects corrected; evidence in reviews/.
- [x] GitHub repository and CI configured.
- [ ] Verify current release publicly on Vercel, configure publishing secrets and demonstrate unattended refresh with retained publication evidence.
- [ ] Configure commercial hosting, domain, operator contact, live analytics and Google publisher approval/consent.
- [ ] Extend personnel, matchup, situational, weather and market intelligence with suitable rights and prospective validation.

The implemented research edition is a foundation for the founding vision. Full acceptance remains open; see launch-acceptance.md.
