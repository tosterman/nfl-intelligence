# Launch acceptance — 2026-09-10

Verdict: publicly deployed research edition; full operational and commercial launch not accepted. Source: https://github.com/tosterman/nfl-intelligence. Live: https://nfl-intelligence-one.vercel.app. Vercel CLI login succeeded on September 10; production is public while previews retain authentication.

## Verified release evidence

Staged release checkpoint: source `1fbc31d1325a75369c11bb9c21cf15d378786e6e` passed [hosted verification 34539746990](https://github.com/tosterman/nfl-intelligence/actions/runs/34539746990): 106 application tests, 229 Python tests, production build and production dependency audit. Recent local evidence covers the weekly revision briefing and return navigation, next-game team cards, metric guide, eight automated accessibility page/width checks, and bounded manual chart/table checks. These changes are on the development branch and are not yet the public edition. Remaining source and operational limitations stay in the coverage table below.

Current hosting limitation: refresh [34526122759](https://github.com/tosterman/nfl-intelligence/actions/runs/34526122759) pushed a new edition but Vercel rejected deployment at its build-rate limit. The public status endpoint remains healthy on the verified edition generated `2026-09-10T20:09:04.084122Z`; the newer Git edition is not accepted as published. Main deletion and non-fast-forward protection are now active, as recorded in `reviews/main-history-protection.md`. Development continues on `internal-development` with automatic deployments disabled for that branch and GitHub checks retained; see `docs/release-batching.md`. Hosting capacity recovery and a subsequent verified publication remain open.

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
| 11 Personnel | Attributed practice/game-designation snapshots and listed QB roles; staged identity-verified historical participation, explicit identifier-conflict notice, reconstructable source bytes and expiry | Individual report dates, confirmed starter changes, snap-weighted player value and validated numerical effects |
| 12 Matchup | Opposing historical efficiency profiles and additive contributions; fixed rate-product interaction experiment rejected after worsening later-season error (reviews/matchup-interaction-results.md) | Validated nonlinear scheme, trench and player interactions |
| 13 Situational | Venue identity, neutral-site adjustment and descriptive prior-game kickoff spacing with completion/timing guards | Validated rest/travel/coaching/schedule effects; the tested rest adjustment remains rejected |
| 14 Weather | Nineteen verified US venue locations using Census address points or attributed OSM stadium bounds, including reviewed official-linked-place reconciliation for Acrisure; eight games with NWS kickoff-hour context in the latest development snapshot; issue/retrieval timestamps, stale/unknown states, compressed source archives | Remaining domestic/international coverage and validated numerical effects |
| 15 Market intelligence | Closing-line benchmark separate from model; verified recent sportsbook observations and first-to-latest movement; staged per-book quote table and timestamped snapshot ranges | Longer history, verified closing capture, CLV and executable-price evidence |
| 16 Time-aware data | Source hashes/times, weekly cutoff, code/configuration identity; missing kickoff withheld | Historical vintage data and additional feed availability timestamps |
| 17 Pipeline | Validated acquisition, fitted artifact, ledger, CI, deployment and receipt workflow; atomic receipt storage, pre-push intent retention, known-cooldown guard, retained input bytes with edition-hash checks, and isolated failure drills (latest safeguards staged) | Sustained scheduled-run reliability and operational recovery from a real provider failure |
| 18 Simulation | Production normal approximation; separate mean-constrained margin and joint-score experiments with settlement constraints; fixed joint evaluation and seven key-margin/tail diagnostics against an overdispersed Gaussian reference | Three-point event representation improves in reused development data, but six other event comparisons are inconclusive; signed-spread/push and prospective calibration remain required before promotion |
| 19–20 Explanation and specific why | Contributions reconcile to margin; historical profiles provide context | Personnel/scheme explanations require missing inputs |
| 21 What changed | Expandable generation revisions; score/margin/total/probability deltas; staged contribution accounting with compatible definitions and reconciliation; model and source identity changes distinguished; staged weekly revision briefing with retained-history links and preserved slate navigation | Verified public history and attribution to specific football inputs |
| 22–24 Homepage, cards, detail | Slate, filters, expected/final distinctions, contextual navigation, analysis and evidence; staged next-scheduled team cards independent of forecast availability | Continued usability tests with actual fans/editorial users |
| 25–29 Design, dark mode, visual language, motion, mobile | Original visual system, self-hosted licensed fonts, reduced-motion treatment, responsive layouts; eight axe page/width checks with no reported violations, plus bounded chart-contrast and table-keyboard follow-up | Physical-device and broader assistive-technology evaluation |
| 30 Accountability | All-game and REG/POST metrics, pushes/ties/no-picks, matched spread/total market benchmarks; separate season-stratified weekly uncertainty audit; prospective grades require receipts; staged plain-language metric guide and data-bound matched-error conclusion | Prospective results after the first verified public pregame capture |
| 31 Calibration | Historical and receipt-qualified prospective Brier/log loss, fixed bins with counts and Wilson 95% intervals, separate live margin/total interval coverage | Actual prospective calibration evidence after eligible results; dependence-aware evaluation as the sample grows |

## Review reconciliation

Independent agents reviewed architecture, numeric integrity and audience experience. Perspectives included statistician, professional bettor, league integrity, media business, fan, skeptical consumer, mobile, accessibility and privacy. These are simulated lenses, not actual interviews with ESPN, the NFL or named public figures. This was not forty independent human or agent reviews.

Confirmed defects fixed: neutral-side symmetry; same-week feature cutoff; misleading publication timestamps; spoofable/tampered receipt evidence; stale/offline provenance; missing kickoff; degenerate probabilities; contribution reconciliation; consent revocation; excessive client data; Rams search alias; filtered counts; week/search return navigation; final-score labeling; 320px toolbar overflow; calibration uncertainty.

Root browser checks used local IAB. Desktop screenshots inspected slate, game, ratings, performance and trust pages. At an actual 320px viewport, slate, game detail, performance, ratings, team hub and methodology measured document width 305px with scrollbar allocation, without document-level horizontal overflow. Ratings intentionally scroll. LAR returned one game. Week 2/Eagles/detail/back restored week and search. Privacy settings focused Decline; approval loaded SDK scripts; revocation reloaded and removed them. This verifies bounded behavior, not live ingestion or full WCAG compliance. The earlier source-only mobile report remains labeled source-only.

## Model result

score-efficiency-v1.2.0: 570 retrospective development games, 569 decisive and one tie; 361 correct winners (63.44%), Brier 0.2204, log loss 0.6309, margin MAE 10.159, total MAE 10.251 and 80% interval coverage 81.23%. Closing-market margin MAE is 9.687 on the same games. Exploratory spread selections: 126 wins, 137 losses, two pushes, 305 no-picks. This does not demonstrate profitable edge. The 2024–25 sample is no longer an untouched holdout. The live graded record remains empty; the first verified public pregame capture now exists, with results still pending.

## External launch gates

Operational update: the forecast publishing workflow is temporarily disabled because its main-branch implementation lacks the staged cooldown guard and its next schedule precedes the provider retry boundary. Odds and health workflows remain active. Restore and verify it using `docs/publication-resume.md`; historical successful runs below do not establish current publisher availability. The new Acrisure integration is staged with 19 verified US venue locations and eight available game weather records at its collection time.

1. Public deployment and exact-artifact capture are verified. Continue production monitoring and broader device/performance verification.
2. The connected Git integration now supports the refresh/deploy/archive workflow without a separate Vercel token. The complete manually dispatched workflow succeeded (34504966362), including GitHub-token push, provider deployment, exact public capture, recovery artifact and receipt push. One actual scheduled five-feed health check is now verified (34524200347); no scheduled odds or forecast run was observed in that audit. Sustained clock-triggered reliability, failure recovery drills and branch protection with an explicit publishing-writer policy remain.
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
