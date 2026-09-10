# Focused matchup usability review

Two independent source-review passes used constructive NFL fan/editorial and skeptical bettor/picky-user lenses. Root reconciled their findings and inspected the actual local browser. These are simulated perspectives, not named NFL/ESPN participants or a full forty-reviewer milestone exercise.

## Confirmed and fixed

- Both reviews found that completed games with retained forecasts could mix actual scores with unqualified probability labels and present-tense prediction prose. Card and detail probabilities now say pregame; completed detail pages use past-tense scoring-profile/margin wording and show the original expected points alongside final scores.
- The skeptical review found missing spread price/time on slate cards. Cards now show the handicap, American price, sportsbook and observed timestamp; existing quote expiry still withholds old prices.
- The skeptical review found divergent sportsbook defaults when FanDuel lacked a spread but another book had one. Both surfaces now use the same spread-bearing default, while explicit detail selections remain available. A changed feed between page requests can still change availability.
- The constructive review found the neutral-game slate/detail mismatch. Detail title, accessible heading and team designations now use vs and designated home/away where appropriate.

## Recommended follow-up

Weather/personnel context is still gated behind model snapshot availability. Decoupling useful independently verified context for future scheduled games remains open; completed pages should continue withholding ineligible pregame context. This was not silently marked complete or implemented as a blanket display of stale reports.

Follow-up: `reviews/pending-game-context.md` records implementation of independently checked context for future scheduled games, with final/started/unknown-kickoff gates and boundary tests. The paragraph above describes the original review finding.

## Verification scope

All 52 application tests and the production build pass. The new server-rendering regression exercises quote price/time, a FanDuel-without-spread fallback shared across card/detail, and expiration. Its first expectation used the internal LA code; it was corrected to the established public LAR label and passed. Local browser inspection verified neutral metadata/designations and pregame labels. The slate's rendered quote fields were inspected, with no document overflow at 1265 CSS pixels and no overflowing quote cells. This is a desktop check, not a new physical-device test. Final games with retained forecasts were source-reviewed; production has no such eligible completed result yet, so no real-result rendering claim is made.

Release `63f1910` received a successful [production deployment](https://vercel.com/khnum/nfl-intelligence/3gPkp7A6uQTQWmKQV9HucNakMGnD), and GitHub verification run `34518111783` passed. Public neutral-matchup HTTP 200 confirmed the title, designated sides and pregame probability label. Public slate HTTP 200 confirmed the timestamp and priced handicap. The first raw-HTML timestamp assertion did not account for React comment separators; stripping those separators made the text check match the actual rendered content.
