# Historical launch evidence

These dated checkpoints preserve their original scope. They do not describe the
current deployment or verification status; use launch-acceptance.md for that.

## Verified release evidence

Current development checkpoint: `5cacb39` passed hosted run
[34628382817](https://github.com/tosterman/nfl-intelligence/actions/runs/34628382817),
including application/Python tests, retained-input replay, Chromium/WebKit
market deadlines, production build and dependency audit. This includes the
independent weather runtime reader, immutable publication, restored history,
and gated collection workflow. A real isolated collection preserved 137 prior
observations and added 14, with all 14 eligible games available and the model
edition unchanged. The 146-file release staging check passed before the
subsequent documentation/evidence updates. None of this establishes public
rollout or sustained scheduled operation. See `docs/weather-runtime-publication.md`.

The preceding `f443fd5` checkpoint passed hosted run 34625851138 with the
reviewed personnel briefing and mobile spacing improvements. The six-player
briefing was reduced from approximately 1096px to 889px without hiding reports.

Earlier completed checkpoint: `b898d2e` passed hosted run
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

## Git integration follow-up — 2026-09-10

The authenticated Vercel project API now confirms a GitHub link to `tosterman/nfl-intelligence`, production branch `main`. This removes the missing repository connection. A post-link push is used to verify the native build path; connection metadata alone is not a successful deployment.

At this inspection, Vercel reports no configured project environment variables and GitHub Actions exposes only the project/org identifier secret names. The odds credential location is being clarified with the owner. The existing refresh workflow still requires its deployment token; native Git deployment does not itself replace the current exact-artifact publication receipt workflow.

## Odds credential resolved

The key was present in ignored local environment configuration. It has now been verified against The Odds API and configured in Vercel production/preview. `reviews/odds-integration.md` records the integration, quota tradeoffs and remaining history/automation work. Prior statements about missing credentials describe the earlier inspection, not this updated state.
