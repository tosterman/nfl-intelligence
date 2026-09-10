# Launch acceptance — 2026-09-10

Verdict: publicly deployed research edition; full operational and commercial launch not accepted. Source: https://github.com/tosterman/nfl-intelligence. Live: https://nfl-intelligence-one.vercel.app. Vercel CLI login succeeded on September 10; production is public while previews retain authentication.

## Verified release evidence

The baseline evidence below is historical. Subsequent releases verified the native refresh/publication workflow, private odds acquisition and recent sportsbook history, and consented Analytics ingestion. Current details are in `reviews/production-monitoring.md`, `reviews/market-history.md`, `reviews/analytics-ingestion.md` and `docs/measurement-plan.md`. The coverage table and external launch gates reflect those updates; early inspection notes at the end retain their original context.

Application baseline: e99b1c3ce22e2095dcada6ebff31d9937e939080. [GitHub CI](https://github.com/tosterman/nfl-intelligence/actions/runs/34493114456) passed 59 Python and 20 TypeScript tests, production build and production dependency audit. This release corrects canonical URLs to the actual production alias and excludes private/source-only files from CLI uploads.

Production deployment dpl_BsD9A7JTgiXZnkJRHoSpWc2ZFrc6 is verified READY through the authenticated API. [Vercel inspector](https://vercel.com/khnum/nfl-intelligence/BsD9A7JTgiXZnkJRHoSpWc2ZFrc6). Its unique hostname is https://nfl-intelligence-e6i3sbfjp-khnum.vercel.app. Anonymous HTTP checks returned 200 for the slate, performance, matchup, status, robots, sitemap, social image and both analytics SDK scripts. The live browser rendered the slate and matchup; consent loaded analytics and Speed Insights scripts. Dashboard event ingestion is not yet verified.

The first publication receipt was captured at 2026-09-10T16:07:16.978840+00:00 after comparing the public deployment's forecast artifact with the intended local release and validating all 105 retained snapshot hashes. This proves capture at that time, not publication of earlier revisions on their generation dates. It does not retroactively qualify the completed New England game.

The exact-release verifier accommodates JavaScript integral-number serialization while retaining canonical local snapshot hashes. Recovery bundles are retained for 90 days in the refresh workflow; concurrent archive pushes retry without force and fail closed on merge conflict. These are tested code paths, not a demonstrated successful production refresh.

## Founding document coverage

| Sections | Implemented evidence | Remaining requirement |
|---|---|---|
| 1–4 Mission, promise, philosophy, constitution | Independent numerical forecasts; visible limitations, uncertainty and methodology | Sustained audience usefulness and prospective accuracy |
| 5 Core outputs | Expected points, margin, total, conditional win probability, fair moneyline and outcome intervals | Empirical discrete score/tie and key-number distributions |
| 6–8 Market, betting language, no edge | Real timestamped The Odds API snapshots; no-vig comparisons, expiry, private immutable archive and missing-market handling; no unvalidated edge claim | Higher-frequency capacity and validated edge policy |
| 9–10 Football model and recency | Opponent-adjusted score model plus EPA, CPOE, sack, turnover and pass-share regression; symmetric neutral matchups | Improvement validated on new data, not reused development results |
| 11 Personnel | Attributed practice/game-designation snapshots and listed QB roles, reconstructable source bytes, scheduled acquisition and matchup context with expiry | Individual report dates, confirmed starter changes, snap-weighted player value and validated numerical effects |
| 12 Matchup | Opposing historical efficiency profiles and additive contributions | Nonlinear scheme, trench and player interactions |
| 13 Situational | Venue identity and neutral-site adjustment | Validated rest/travel/coaching/schedule effects |
| 14 Weather | Sixteen verified US venue locations using Census address points or attributed OSM stadium bounds; seven currently eligible games with NWS kickoff-hour context; issue/retrieval timestamps, stale/unknown states, compressed source archives | Remaining domestic/international coverage and validated numerical effects |
| 15 Market intelligence | Closing-line benchmark separate from model; verified recent sportsbook observations and first-to-latest spread movement | Longer history, verified closing capture, CLV and executable-price evidence |
| 16 Time-aware data | Source hashes/times, weekly cutoff, code/configuration identity; missing kickoff withheld | Historical vintage data and additional feed availability timestamps |
| 17 Pipeline | Validated acquisition, fitted artifact, ledger, CI, deployment and receipt workflow | Sustained scheduled-run reliability and failure recovery drills |
| 18 Simulation | Production normal approximation; separate mean-constrained discrete-distribution experiments with settlement constraints and prior-only tie estimates | Validate tails/key numbers and joint scores before promotion; experimental gains remain inconclusive |
| 19–20 Explanation and specific why | Contributions reconcile to margin; historical profiles provide context | Personnel/scheme explanations require missing inputs |
| 21 What changed | Expandable generation revisions; score/margin/total/probability deltas; model, configuration and source identity changes distinguished | Verified public history and attribution to specific football inputs |
| 22–24 Homepage, cards, detail | Slate, filters, expected/final distinctions, contextual navigation, analysis and evidence | Continued usability tests with actual fans/editorial users |
| 25–29 Design, dark mode, visual language, motion, mobile | Original visual system, self-hosted licensed fonts, reduced-motion treatment, responsive layouts | Physical-device and broader assistive-technology evaluation |
| 30 Accountability | All-game and REG/POST metrics, pushes/ties/no-picks, matched spread/total market benchmarks; prospective grades require receipts | Prospective results after the first verified public pregame capture |
| 31 Calibration | Historical and receipt-qualified prospective Brier/log loss, fixed bins with counts and Wilson 95% intervals, separate live margin/total interval coverage | Actual prospective calibration evidence after eligible results; dependence-aware evaluation as the sample grows |

## Review reconciliation

Independent agents reviewed architecture, numeric integrity and audience experience. Perspectives included statistician, professional bettor, league integrity, media business, fan, skeptical consumer, mobile, accessibility and privacy. These are simulated lenses, not actual interviews with ESPN, the NFL or named public figures. This was not forty independent human or agent reviews.

Confirmed defects fixed: neutral-side symmetry; same-week feature cutoff; misleading publication timestamps; spoofable/tampered receipt evidence; stale/offline provenance; missing kickoff; degenerate probabilities; contribution reconciliation; consent revocation; excessive client data; Rams search alias; filtered counts; week/search return navigation; final-score labeling; 320px toolbar overflow; calibration uncertainty.

Root browser checks used local IAB. Desktop screenshots inspected slate, game, ratings, performance and trust pages. At an actual 320px viewport, slate, game detail, performance, ratings, team hub and methodology measured document width 305px with scrollbar allocation, without document-level horizontal overflow. Ratings intentionally scroll. LAR returned one game. Week 2/Eagles/detail/back restored week and search. Privacy settings focused Decline; approval loaded SDK scripts; revocation reloaded and removed them. This verifies bounded behavior, not live ingestion or full WCAG compliance. The earlier source-only mobile report remains labeled source-only.

## Model result

score-efficiency-v1.2.0: 570 retrospective development games, 569 decisive and one tie; 361 correct winners (63.44%), Brier 0.2204, log loss 0.6309, margin MAE 10.159, total MAE 10.251 and 80% interval coverage 81.23%. Closing-market margin MAE is 9.687 on the same games. Exploratory spread selections: 126 wins, 137 losses, two pushes, 305 no-picks. This does not demonstrate profitable edge. The 2024–25 sample is no longer an untouched holdout. The live graded record remains empty; the first verified public pregame capture now exists, with results still pending.

## External launch gates

1. Public deployment and exact-artifact capture are verified. Continue production monitoring and broader device/performance verification.
2. The connected Git integration now supports the refresh/deploy/archive workflow without a separate Vercel token. The complete manually dispatched workflow succeeded (34504966362), including GitHub-token push, provider deployment, exact public capture, recovery artifact and receipt push. Sustained clock-triggered reliability, failure recovery drills and branch protection with an explicit publishing-writer policy remain.
3. Web Analytics is now enabled and consented production pageviews are verified through the reporting API. A declined control page remained untracked in the bounded check. Speed Insights reports received data; representative performance remains unverified. Custom-event reporting is blocked by the current plan. See `reviews/analytics-ingestion.md` and `docs/measurement-plan.md` for exact evidence and limitations.
4. Confirm operator identity, private contact channel and final domain. The authenticated team API reports Hobby; a hosting plan permitting commercial use is required before monetization. No recurring service was purchased.
5. Obtain Google publisher approval and applicable certified consent configuration before enabling ad tags/ads.txt. AdSense/Ad Manager monetizes publisher inventory; Google Ads buys advertising. See monetization.md.
6. Add the missing inputs and demonstrate their benefit before presenting this as complete football intelligence.

No claim of perfect quality, Google approval, sustained scheduler reliability or revenue is made. The goal remains open.

## Git integration follow-up — 2026-09-10

The authenticated Vercel project API now confirms a GitHub link to `tosterman/nfl-intelligence`, production branch `main`. This removes the missing repository connection. A post-link push is used to verify the native build path; connection metadata alone is not a successful deployment.

At this inspection, Vercel reports no configured project environment variables and GitHub Actions exposes only the project/org identifier secret names. The odds credential location is being clarified with the owner. The existing refresh workflow still requires its deployment token; native Git deployment does not itself replace the current exact-artifact publication receipt workflow.

## Odds credential resolved

The key was present in ignored local environment configuration. It has now been verified against The Odds API and configured in Vercel production/preview. `reviews/odds-integration.md` records the integration, quota tradeoffs and remaining history/automation work. Prior statements about missing credentials describe the earlier inspection, not this updated state.
