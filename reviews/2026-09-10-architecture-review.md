# Architecture review — 2026-09-10

Reviewed `founding.docx` (all 31 sections), `docs/design.md`, and `docs/implementation-plan.md`. This is a design checkpoint, not a code or deployed-system acceptance. The perspectives below simulate a statistician, professional sports bettor, league-integrity executive, and media-business operator; no real person or organization has endorsed the work.

## Verdict

The proposed Python-to-static-JSON architecture is a good first production architecture: cheap to serve, reproducible, inspectable, and sufficient for a useful weekly publication. It can honestly deliver an opponent-adjusted score baseline and a public research laboratory. It cannot yet fulfill the founding document's ultimate personnel, matchup, forecast-weather, current-market, and historical-change intelligence promises. Explicitly labeling those modules unavailable is appropriate; describing the entire founding constitution as completed would not be.

The most important product decision is to publish a trustworthy baseline whose limitations are visible beside each prediction. A polished percentage should not imply that the system knows today's quarterback availability.

## P0 — required before trustworthy public predictions

1. **Availability is not the same as date ordering.** A record with kickoff before the forecast cutoff can still be in progress. Filter training observations to demonstrably completed and available before prediction time. When historical availability times are missing, use a documented conservative lag and call the exercise a retrospective replay. Never silently reuse final season aggregates or final-week ratings. Freeze source bytes, code revision, parameters, feature cutoff, and model version. A modern download of revised historical scores is not an archived contemporary source.

   Acceptance: changing target or future results leaves the target forecast unchanged; a Thursday forecast cannot see Thursday's eventual final result; the same raw-byte artifact and cutoff reproduce the same prediction. A recent historical download remains labeled retrospective even when chronological filtering passes.

2. **All fitted quantities need chronological isolation.** Ridge penalty and decay are only part of fitting. Home advantage, scoring intercept, residual variance, win calibration, interval widths, edge thresholds, and any clipping rules must be chosen without the held-out outcomes. Keep a declared training period, tuning period, and untouched evaluation period. Walk-forward refitting on earlier observed outcomes is valid when the procedure was fixed in advance. Repeatedly inspecting the holdout to choose a better model consumes that holdout.

   Acceptance: export season-by-season sample counts, parameters and train/tune/test boundaries; label the exact model-selection process; report Brier score, log loss, margin/total MAE, interval coverage and naive baselines on the same eligible games. Calibration bins need counts and uncertainty, not only a diagonal chart. Separate REG/POST and disclose treatment of ties.

3. **Hashing does not itself prove pregame publication.** A hash proves content identity, not when the public could see it. Git history is useful audit evidence but is mutable by sufficiently privileged users. Distinguish generatedAt, sourceRetrievedAt, forecastAsOf, and publishedAt. Append a new forecast revision instead of editing an existing object. Select the scoring snapshot by a fixed rule, such as the latest successfully published snapshot before the declared cutoff. Record missed games; never backfill them into live performance.

   Acceptance: previous snapshot bytes remain unchanged; final-result ingestion changes only a results record; a post-kickoff first publication is refused; a failed deploy cannot count as a published pregame prediction; a historical replay cannot enter live totals. Use protected history and retained publication receipts. Stronger independent timestamping can follow, but avoid calling ordinary Git an absolute immutability guarantee.

## P1 — model usefulness and sports-bettor scrutiny

4. **Neutral games and season transitions need explicit behavior.** Do not give the designated home team normal home advantage at a neutral venue. Handle franchise aliases consistently, season boundaries, insufficient training history, and postponed/canceled games. Recency should have an explicit time unit, with offseason behavior documented. The system must not present stale roster-era strength as current personnel knowledge.

5. **Mean score is not the most likely exact score.** Label decimal scores as expected points. A residual model must distinguish outcome prediction intervals from uncertainty in the estimated mean. A symmetric margin distribution may be an initial approximation, but do not use it to claim accurate integer spread pushes, ties, or NFL key-number probabilities without validating them. State whether home win probability excludes, splits, or separately models ties; fair moneyline must use settlement-consistent probabilities. Audit score arithmetic after any clipping or rounding.

6. **Market disagreement is not demonstrated expected profit.** A two-point margin gap lacks a cover probability and offered price. For a settled one-unit stake with decimal odds d, expected net return is p(win)*(d-1)-p(loss), with pushes returning the stake. Do not treat a no-vig consensus probability as an actually purchasable price. Store sportsbook, market type, line, both side prices, observation time, and settlement rules. Reject stale or mismatched quotes. Historical closing-price comparisons are research benchmarks, not evidence a user could have placed the displayed price at the forecast cutoff.

7. **Selectivity must be visible.** Report all eligible predictions, abstentions and unavailable-data counts. If only certain edges are scored, publish the selection rule and full-universe comparison. CLV needs matched market, timestamp, line and price conventions. Confidence should communicate validated reliability or data completeness; a large favorite is not automatically a well-supported prediction. Avoid a profitability claim based on a small subset or best season.

8. **Contribution arithmetic is not causal explanation.** Ridge offensive and defensive terms can explain the model's score, but cannot establish why a particular player, scheme, or injury caused it. Generate factual prose from the exact terms in the artifact. If QB, OL/DL, weather and injury modules are absent, their contributions must stay unavailable, not become zero-valued evidence that these factors have no effect. Display the baseline/scoring intercept in any score decomposition and define positive/negative signs explicitly.

## P1 — integrity and commercial operation

9. **Track rights per asset and source, not per ecosystem.** The nflverse data repository identifies CC BY 4.0, while the nflverse software package has an MIT license; those are different objects. Participation data have their own attribution and licensing notes. These sources demonstrate why the implementation must record the exact downloaded dataset's license and upstream conditions rather than claim that all football data are covered by one license. The `nfldata` README examined here does not itself establish a comprehensive commercial redistribution permission. Attribution should name the actual source; logos, photographs, market feeds and player/personnel feeds each need their own decision. Use text team identifiers while artwork rights remain unverified. [nflverse-data repository](https://github.com/nflverse/nflverse-data), [software license](https://nflverse.nflverse.com/LICENSE.html), [participation-data documentation](https://nflreadr.nflverse.com/reference/load_participation.html), [nfldata README](https://raw.githubusercontent.com/nflverse/nfldata/master/README.md).

10. **Advertising readiness is external and content-specific.** Google distinguishes publisher restrictions from prohibition: restricted inventory can receive fewer or no bids. Its online-gambling section includes gambling-promoting affiliate/aggregator pages and jurisdiction exclusions. This does not establish that an independent analytics page is prohibited or approved. Avoid guarantees, keep sportsbook affiliate links disabled until separately reviewed, and treat ads as a later configuration. Original editorial analysis, clear authorship, corrections, contact, source documentation, and useful public performance reporting support the media proposition. Ad slots alone do not create a monetizable business. [Google Publisher Restrictions](https://support.google.com/adsense/answer/10437795?hl=en).

11. **Keep editorial and revenue incentives separate.** The league-integrity lens requires prominent independence, no suggestion of official affiliation or insider access, a documented correction process, and no fabricated injury assertions. The business lens requires measuring returning weekly readers and useful game-detail engagement before projecting advertising revenue. Ads must be visually distinguishable from verdicts and must not obstruct mobile analysis. “Informational use” copy cannot substitute for truthful claims or policy compliance.

## Release scope and evidence

Ship as a baseline research preview if P0 gates pass. Display coverage limitations on slate and game pages, not only the methodology page. Make “No verified market feed” distinct from “No meaningful edge”: the first means the comparison cannot be made. The first live performance report should legitimately begin empty.

Before calling the platform an operational intelligence service, add licensed timestamped market and personnel inputs, empirical distribution/calibration validation, public forecast revision navigation, and alerting when scheduled refresh/publication fails. A static website can support these additions; a database migration is not a prerequisite for proving the model's usefulness.

The next review should inspect actual engine code, exported evidence and the deployed ledger; none of those implementation checks are certified by this document.
