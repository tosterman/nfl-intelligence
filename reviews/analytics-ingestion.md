# Analytics ingestion verification — 2026-09-10

The initial authenticated `visits/count` request returned HTTP 400: Web Analytics was not enabled for this project. Project metadata contained a webAnalytics identifier, which did not establish activation or data receipt. `vercel project web-analytics nfl-intelligence --format json --scope khnum` returned enabled=true for the correct project. A fresh count then returned zero pageviews, establishing the pre-test baseline.

The production browser opened methodology, used Privacy settings → Allow analytics, and navigated to Power ratings. Both analytics SDK scripts were present after consent. The reporting API then returned one provider-reported visitor and two pageviews. These were controlled QA visits, not organic traffic.

The responsible-use path had zero visits before the negative control. Privacy settings → Decline reloaded the site; navigation to Responsible use showed no analytics SDK scripts in the DOM. Subsequent authenticated path-filtered counts remained zero. This bounded negative control and code review support the consent behavior; they are not a guarantee about all browsers or a comprehensive legal compliance audit.

The custom-events count endpoint returned HTTP 402 with the requirement for Enterprise or Pro. Official documentation agrees. Existing `track()` calls therefore establish instrumentation only; working custom-event reporting is not claimed. The current SDK/callback code is retained for commercial-plan activation. No paid plan was purchased. Speed Insights metadata hasData=true and dataReceivedAt=1789056461776, which proves received data but not representative Core Web Vitals.

The new owner report ran against the live API for September 4–11 UTC (current day partial). It reported 2 pageviews, 1 provider-reported visitor, 1 methodology pageview, zero game/record pageviews, and plan-restricted custom events. Ratios describe pageview mix. The first live report also exposed UTC-day rounding and Windows command-shim handling; both were corrected before the successful run. Report artifacts remain ignored/private rather than publishing traffic or credentials to GitHub.

Authoritative references: https://vercel.com/docs/analytics/web-analytics-api and https://vercel.com/docs/analytics/custom-events . Dashboard browser login was unavailable, so the same-data reporting API supplied receipt evidence; no screenshot of a logged-in dashboard is claimed.

Independent adversarial review found no material reporting or command-invocation issue. It verified the pageview denominator, unknown-versus-zero handling, effective-window check and ignored aggregate output. Both new report tests passed, and the complete Python suite passed 71 tests.
