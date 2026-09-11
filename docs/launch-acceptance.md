# Launch acceptance — 2026-09-11

Verdict: the public research edition is available; the full operational and
commercial launch is not accepted. Repository:
https://github.com/tosterman/nfl-intelligence. Public site:
https://nfl-intelligence-one.vercel.app.

## Current verified state

- Direct endpoint checks on September 11 returned the public model edition
  generated September 10 at 20:09 UTC and the local edition generated September
  11 at 16:17 UTC. The public deployment has not caught up with development.
  Exact responses are in `reviews/launch-current-state.json`.
- A later read-only comparison in `reviews/launch-feed-check.json` verified all
  seven local feed checks and the intended edition identity. The older public
  site still served a different, earlier edition: forecast and odds checks
  passed, while personnel, weather, quarterback, matchup and participation
  checks failed. Public release acceptance requires resolving those failures;
  local health does not resolve the public incident.
- Personnel runtime restore, real acquisition, independent replay, immutable
  incremental publication and local readback are verified. The combined run
  selected publication `99096b70eaf7bd295b9dbb180efd06b421bd69cb2e92449f5d9752d065f92b28`
  with 21 new objects and 310 reused. Degraded operation was tested separately
  with simulated failures, without presenting those failures as real feed data.
  See `docs/personnel-runtime-publication.md` for exact evidence and limitations.
- Weather runtime v2 and bounded game-history restoration work locally. The
  public reader rollout and actual scheduled execution remain unverified.
- Hosted verification passed on `ef0fb2f` in run
  [34641664018](https://github.com/tosterman/nfl-intelligence/actions/runs/34641664018).
  The subsequent generated-benchmark staging fix passed 23 related local checks;
  its hosted run was still running at the 20:01 UTC inspection.
- The real market benchmark now exports retained captures, replays the pinned
  calculation without networking, verifies its private recovery package and
  atomically replaces the local summary. Its September 11 19:56 UTC run has
  zero eligible paired games; exclusions are explicit rather than treated as
  zero error. At 20:02 UTC, Chromium and WebKit verified the intended report
  fingerprint and rendered counts at 320px with no scoped axe violations,
  browser errors or document overflow. A deliberately wrong fingerprint was
  rejected against the actual local page. See `docs/market-benchmark.md` and
  `reviews/market-benchmark-browser.json`. Public rollout and scheduled
  benchmark execution remain unverified; its enabling variable is unset.
- The forecast workflow remains disabled. Live workflow inspection shows odds
  and health active. Weather and personnel workflows are gated in development;
  their enabling variables remain unset. No sustained reliability claim follows
  from successful manual runs.
- Vercel deployment retries remain deferred until the recorded September 11
  20:25:03 UTC boundary, followed by a fresh eligibility check. Follow
  `docs/publication-resume.md`; do not infer deployment from a Git push.

The weekly briefing now includes verified personnel and weather comparisons
alongside model revisions, with separate timestamps, before/after weather values,
expiry and no invented numerical effects. Local Chromium/WebKit checks at 320px
passed; see `reviews/weekly-context-briefing.md`. Actual audience comprehension,
prospective model evidence and the commercial gates below remain outstanding.

Earlier release and credential-discovery notes have moved to
[historical launch evidence](launch-evidence-history.md). They retain their
original claims and dates; they are not current operational status.

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

score-efficiency-v1.2.0: 570 retrospective development games, 569 decisive and one tie; 361 correct winners (63.44%), Brier 0.2204, log loss 0.6309, margin MAE 10.159, total MAE 10.251 and 80% interval coverage 81.23%. Closing-market margin MAE is 9.687 on the same games. Exploratory spread selections: 126 wins, 137 losses, two pushes, 305 no-picks. This does not demonstrate profitable edge. The 2024–25 sample is no longer an untouched holdout. The receipt-qualified live record currently has zero eligible grades and two missed games. Completed results lacked the required original context and pregame publication evidence; no old snapshot was backfilled.

## External launch gates

Operational update: the forecast publishing workflow is temporarily disabled because its main-branch implementation lacks the staged cooldown guard and its next schedule precedes the provider retry boundary. Odds and health workflows remain active. Restore and verify publishing using `docs/publication-resume.md`; historical successful runs below do not establish current publisher availability. The experimental planned odds collector must also remain inactive until acquisition-history completeness and migration are established. Missing live history cannot be initialized as an empty budget.

1. An older public deployment and its exact-artifact capture were verified. The current development release remains unpublished; the older public weather incident requires a verified rollout. Continue broader device/performance verification.
2. The connected Git integration now supports the refresh/deploy/archive workflow without a separate Vercel token. The complete manually dispatched workflow succeeded (34504966362), including GitHub-token push, provider deployment, exact public capture, recovery artifact and receipt push. One actual scheduled five-feed health check is now verified (34524200347); no scheduled odds or forecast run was observed in that audit. Sustained clock-triggered reliability, failure recovery drills and branch protection with an explicit publishing-writer policy remain.
3. Web Analytics is now enabled and consented production pageviews are verified through the reporting API. A declined control page remained untracked in the bounded check. Speed Insights reports received data; representative performance remains unverified. Custom-event reporting is blocked by the current plan. See `reviews/analytics-ingestion.md` and `docs/measurement-plan.md` for exact evidence and limitations.
4. Confirm operator identity, private contact channel and final domain. The authenticated team API reports Hobby; a hosting plan permitting commercial use is required before monetization. No recurring service was purchased.
5. Obtain Google publisher approval and applicable certified consent configuration before enabling ad tags/ads.txt. AdSense/Ad Manager monetizes publisher inventory; Google Ads buys advertising. See monetization.md.
6. Add the missing inputs and demonstrate their benefit before presenting this as complete football intelligence.

No claim of perfect quality, Google approval, sustained scheduler reliability or revenue is made. The goal remains open.
