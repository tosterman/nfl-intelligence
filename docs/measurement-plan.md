# Measurement and revenue evidence

## What works now

Web Analytics is enabled for the Vercel project. Consented production pageview ingestion was verified on September 10, 2026 through Vercel's authenticated reporting API. Speed Insights project metadata reports received data, but no statistically meaningful performance sample has been established. Code loading, ingestion, representative performance and business success are different checkpoints.

Run `python scripts/analytics_report.py` with an authenticated Vercel CLI. It makes read-only requests for this project, writes an aggregated report to ignored `release-recovery/analytics-report.json`, and prints the same result. No Vercel token is stored in the repository. The window is six prior UTC calendar days plus the current partial UTC day. The script checks the effective response window rather than combining unlike time ranges. Provider failures and plan restrictions remain explicit statuses; they are never converted into zero counts.

The current measurements include QA visits. They demonstrate collection, not organic audience traction. Opt-in analytics exclude people who decline; browser blocking and provider filtering also affect coverage. Provider-reported visitors are not verified unique people or evidence of long-term retention.

| Measure | Definition | Decision it supports | Limit |
| --- | --- | --- | --- |
| Consented production pageviews | Vercel visits count for the fixed report window | Whether readership is growing after launch | Includes repeat views and QA; misses declined analytics |
| Provider-reported visitors | Vercel visitor count for that same window | Audience scale within provider methodology | Not authenticated customers or cross-period retention |
| Game-page share | `/games/` pageviews / all pageviews | Whether matchups receive readership | Content mix, not a visitor conversion funnel |
| Track-record share | `/performance` pageviews / all pageviews | Whether readers inspect accountability | Does not prove understanding or trust |
| Methodology share | `/methodology` pageviews / all pageviews | Whether readers inspect assumptions | Does not prove comprehension |
| Product interactions | `game_open`, `spotlight_open`, `slate_filter`, `market_book_selected` | Discovery and comparison behavior | Instrumented with consent; reporting requires Pro/Enterprise and is currently unavailable |

Do not infer a click-through funnel from these aggregate page counts. Direct visits, repeat views, multiple entrances and changing consent break that interpretation. No search terms or user-entered text are attached to custom events. Analytics URL query strings and fragments are removed before sending.

## Revenue activation

Audience revenue and model performance must remain separate. A profitable publishing business does not prove profitable predictions. Model upgrades require the existing prospective evidence and validation gates.

Once an approved publisher account, commercial hosting, operator identity/contact, domain and consent configuration exist, use the publisher's own impression, revenue and pageview definitions for ad reporting. Never divide publisher revenue by this site's opt-in analytics pageviews and label the result publisher RPM. Reconcile reporting period, timezone, invalid-traffic adjustments and currency before calculating results. Keep estimated earnings separate from finalized revenue and cash received.

Before claiming monetization readiness, verify real publisher reporting, ads eligibility, applicable consent behavior, mobile layout stability with filled and unfilled slots, and a revenue reconciliation. Ads remain disabled today. No paid hosting or analytics upgrade was purchased during verification.

## Operating checks

`/api/status` measures forecast/source freshness; `/api/odds-status` measures stored acquisition freshness. Neither proves full bookmaker coverage. The odds workflow checks authenticated collection and exact archive readback. Track operational failures independently from readership metrics. A green pipeline is not a model accuracy claim.

References: [Web Analytics API](https://vercel.com/docs/analytics/web-analytics-api), [custom-event plan availability](https://vercel.com/docs/analytics/custom-events), [analytics privacy](https://vercel.com/docs/analytics/privacy-policy). Live evidence is in `reviews/analytics-ingestion.md`.
