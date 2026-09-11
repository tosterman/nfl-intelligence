# Launch acceptance — 2026-09-11

Verdict: publicly deployed research edition; full operational and commercial launch not accepted. Source: https://github.com/tosterman/nfl-intelligence. Live: https://nfl-intelligence-one.vercel.app. Vercel CLI login succeeded on September 10; production is public while previews retain authentication.

## Verified release evidence

Latest completed checkpoint: `b898d2e` passed hosted run
[34623432915](https://github.com/tosterman/nfl-intelligence/actions/runs/34623432915):
188 application tests, 341 Python tests, current-edition explanation verification,
retained-input replay, browser deadline checks, production build and dependency
audit. This includes season-aware participation collection, identity binding and
local display, plus the real-result refresh and retained total explanations.
The subsequent `ccf5096` adds a nonempty display test and stable binding fixtures;
its focused tests and type check passed locally. Publication remains outstanding.

Current-season participation has no eligible Week 1 sample; this is expected,
not zero participation. Four local browser cases and independent source review
cover its empty state and stale/report-rollover guards. A nonempty isolated
rendering test is distinct from real future-week evidence.

The earlier release checkpoints below retain their original verification scope.

Latest completed development verification: `60964d3` passed GitHub run
[34618803803](https://github.com/tosterman/nfl-intelligence/actions/runs/34618803803),
including retained-input replay, application/Python tests, browser deadline
checks, production build and dependency audit. All 324 Python tests also passed
locally. This includes retained total and weather explanations, the opening
brief, slate weather/comparisons and staged-release verification.

The subsequent Highmark checkpoint `cc9e2dd` adds a verified 2026 stadium-area
location and refreshes real weather to 14 games and 137 retained observations.
It passed local source replay, venue/season tests, six Chromium/WebKit checks
and the 319-page production build. Its hosted run
[34620242767](https://github.com/tosterman/nfl-intelligence/actions/runs/34620242767)
completed successfully. These changes are not publicly deployed.

The older checkpoints below are historical evidence, not the current head.

Latest completed hosted checkpoint: source `1c71606` passed [verification 34608780005](https://github.com/tosterman/nfl-intelligence/actions/runs/34608780005). It includes historical matchup comparisons, the experimental journaled odds collector, reusable input archives with offline numerical replay, verified source-record explanations, and kickoff-aware homepage status. The workflow includes application/Python tests, browser deadline checks, a production build and dependency checks. Subsequent mobile-layout work is verified separately in `reviews/mobile-matchup-hierarchy.md`. Development-branch changes are not the public edition.

At 2026-09-11 13:34 UTC, the public status endpoint returned `ok` for the older edition generated `2026-09-10T20:09:04.084122+00:00`. At 13:33 UTC, a read-only check confirmed the live acquisition reservation was still absent. That is not evidence of zero historical usage. The planned collector remains disconnected from routes and schedules; see `reviews/planned-odds-executor.md` and `reviews/odds-reservation-observation.json`.

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
| 12 Matchup | Opposing efficiency profiles; independently acquired current-season and prior-season big-play/inside-20 samples; exact-source replay, sample sizes, expiry, season scope and explicit empty states. Twelve local mobile/desktop browser cases passed. Rate-product model interaction experiment remains rejected | Hosted scheduled rollover and real positive current-season samples remain unverified; descriptive comparisons are not validated nonlinear scheme, trench or player effects |
| 13 Situational | Venue identity, neutral-site adjustment and descriptive prior-game kickoff spacing with completion/timing guards | Validated rest/travel/coaching/schedule effects; the tested rest adjustment remains rejected |
| 14 Weather | Twenty-five verified US venue locations using Census address points or attributed OSM stadium bounds, including reviewed official-linked-place reconciliation for Acrisure and the new Highmark stadium; fourteen games with NWS kickoff-hour context in the retained development snapshot; issue/retrieval timestamps, stale/unknown states, compressed source archives | Remaining domestic/international coverage and validated numerical effects |
| 15 Market intelligence | Closing-line benchmark separate from model; verified recent sportsbook observations and first-to-latest movement; staged per-book quote table and timestamped snapshot ranges | Longer history, verified closing capture, CLV and executable-price evidence |
| 16 Time-aware data | Source hashes/times, weekly cutoff, code/configuration identity; missing kickoff withheld | Historical vintage data and additional feed availability timestamps |
| 17 Pipeline | Validated acquisition, fitted artifact, ledger, CI, deployment and receipt workflow; atomic receipt storage, pre-push intent retention, known-cooldown guard, retained input bytes with edition-hash checks, and isolated failure drills (latest safeguards staged) | Sustained scheduled-run reliability and operational recovery from a real provider failure |
| 18 Simulation | Production normal approximation; separate joint-score experiments, key-margin/tail diagnostics and completed signed-spread/total settlement audit over 285 games | All four settlement comparison intervals include zero; sparse spread pushes and no integer totals cannot establish push calibration. Prospective evidence remains required before promotion |
| 19–20 Explanation and specific why | Contributions reconcile to margin; retained total accounting replays the exact frozen engine and input bundle; opening brief identifies leading/opposing terms and market differences; historical and weekly profiles provide separate descriptive context | Personnel/scheme explanations require missing inputs; structured evidence drives current explanations rather than a deployed generative explanation layer |
| 21 What changed | Expandable generation revisions; score/margin/total/probability deltas; staged contribution accounting with compatible definitions and reconciliation; model and source identity changes distinguished; staged weekly revision briefing with retained-history links and preserved slate navigation | Verified public history and attribution to specific football inputs |
| 22–24 Homepage, cards, detail | Slate, filters, expected/final distinctions, contextual navigation, analysis and evidence; next-scheduled team cards; selected-book spread/total differences; kickoff weather with expiry and explicit outdoor scope | Continued usability tests with actual fans/editorial users |
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

Operational update: the forecast publishing workflow is temporarily disabled because its main-branch implementation lacks the staged cooldown guard and its next schedule precedes the provider retry boundary. Odds and health workflows remain active. Restore and verify publishing using `docs/publication-resume.md`; historical successful runs below do not establish current publisher availability. The experimental planned odds collector must also remain inactive until acquisition-history completeness and migration are established. Missing live history cannot be initialized as an empty budget.

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
