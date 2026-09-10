# Launch acceptance — 2026-09-10

Verdict: implemented research edition; public operational and commercial launch not accepted. Source: https://github.com/tosterman/nfl-intelligence. Vercel deployment creation succeeded, but its URLs require login and the connected account returns 404 for deployment status. No READY state, public rendering, analytics ingestion or prospective publication receipt is claimed.

## Founding document coverage

| Sections | Implemented evidence | Remaining requirement |
|---|---|---|
| 1–4 Mission, promise, philosophy, constitution | Independent numerical forecasts; visible limitations, uncertainty and methodology | Sustained audience usefulness and prospective accuracy |
| 5 Core outputs | Expected points, margin, total, conditional win probability, fair moneyline and outcome intervals | Empirical discrete score/tie and key-number distributions |
| 6–8 Market, betting language, no edge | Tested no-vig, quote freshness and settlement contracts; unavailable differs from no edge | Licensed timestamped quotes and validated edge policy |
| 9–10 Football model and recency | Opponent-adjusted score model plus EPA, CPOE, sack, turnover and pass-share regression; symmetric neutral matchups | Improvement validated on new data, not reused development results |
| 11 Personnel | Explicit unavailable coverage state | Current availability, starter changes, snap-weighted player value, rights and timestamps |
| 12 Matchup | Opposing historical efficiency profiles and additive contributions | Nonlinear scheme, trench and player interactions |
| 13 Situational | Venue identity and neutral-site adjustment | Validated rest/travel/coaching/schedule effects |
| 14 Weather | Explicit unavailable state | Archived forecast-at-kickoff inputs and validated effects |
| 15 Market intelligence | Closing-line benchmark separate from model | Price history, movement, CLV and executable-price evidence |
| 16 Time-aware data | Source hashes/times, weekly cutoff, code/configuration identity; missing kickoff withheld | Historical vintage data and additional feed availability timestamps |
| 17 Pipeline | Validated acquisition, fitted artifact, ledger, CI, deployment and receipt workflow | Authenticated production deployment and successful unattended run |
| 18 Simulation | Analytic normal residual approximation, explicitly labeled | Discrete outcome simulation only if it improves validation |
| 19–20 Explanation and specific why | Contributions reconcile to margin; historical profiles provide context | Personnel/scheme explanations require missing inputs |
| 21 What changed | Generation revisions exposed on game page | Verified public revision history and input-change attribution |
| 22–24 Homepage, cards, detail | Slate, filters, expected/final distinctions, contextual navigation, analysis and evidence | Continued usability tests with actual fans/editorial users |
| 25–29 Design, dark mode, visual language, motion, mobile | Original visual system, self-hosted licensed fonts, reduced-motion treatment, responsive layouts | Physical-device and broader assistive-technology evaluation |
| 30 Accountability | All-game metrics, pushes/ties/no-picks, market benchmark; prospective grades require receipts | Genuine public pregame predictions and results |
| 31 Calibration | Brier/log loss, bins with counts and Wilson 95% intervals, interval coverage | Prospective calibration |

## Review reconciliation

Independent agents reviewed architecture, numeric integrity and audience experience. Perspectives included statistician, professional bettor, league integrity, media business, fan, skeptical consumer, mobile, accessibility and privacy. These are simulated lenses, not actual interviews with ESPN, the NFL or named public figures. This was not forty independent human or agent reviews.

Confirmed defects fixed: neutral-side symmetry; same-week feature cutoff; misleading publication timestamps; spoofable/tampered receipt evidence; stale/offline provenance; missing kickoff; degenerate probabilities; contribution reconciliation; consent revocation; excessive client data; Rams search alias; filtered counts; week/search return navigation; final-score labeling; 320px toolbar overflow; calibration uncertainty.

Root browser checks used local IAB. Desktop screenshots inspected slate, game, ratings, performance and trust pages. At an actual 320px viewport, slate, game detail, performance, ratings, team hub and methodology measured document width 305px with scrollbar allocation, without document-level horizontal overflow. Ratings intentionally scroll. LAR returned one game. Week 2/Eagles/detail/back restored week and search. Privacy settings focused Decline; approval loaded SDK scripts; revocation reloaded and removed them. This verifies bounded behavior, not live ingestion or full WCAG compliance. The earlier source-only mobile report remains labeled source-only.

## Model result

score-efficiency-v1.2.0: 570 retrospective development games, 569 decisive and one tie; 361 correct winners (63.44%), Brier 0.2204, log loss 0.6309, margin MAE 10.159, total MAE 10.251 and 80% interval coverage 81.23%. Closing-market margin MAE is 9.687 on the same games. Exploratory spread selections: 126 wins, 137 losses, two pushes, 305 no-picks. This does not demonstrate profitable edge. The 2024–25 sample is no longer an untouched holdout. The live record remains empty pending public pregame evidence.

## External launch gates

1. Authenticate the correct Vercel project/account; verify READY and anonymously accessible pages, headers, artifact and status endpoint.
2. Configure VERCEL_TOKEN, VERCEL_ORG_ID and VERCEL_PROJECT_ID repository secrets; demonstrate refresh/deploy/archive, recovery and failure alerting. Set branch protection with an explicit publishing-writer policy.
3. Enable analytics and Speed Insights; verify consented event receipt, absent declined events and production performance.
4. Confirm operator identity, private contact channel, final domain and hosting plan permitting commercial use. No recurring service was purchased.
5. Obtain Google publisher approval and applicable certified consent configuration before enabling ad tags/ads.txt. AdSense/Ad Manager monetizes publisher inventory; Google Ads buys advertising. See monetization.md.
6. Add the missing inputs and demonstrate their benefit before presenting this as complete football intelligence.

No claim of perfect quality, Google approval, operational automation or revenue is made. The goal remains open.
