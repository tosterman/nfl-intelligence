# Context before a model forecast

Future scheduled games without a model snapshot now expose weather and personnel context independently. The existing weather, personnel and quarterback eligibility functions still determine source freshness, schedule/season/week/team matching and role availability. The page supplies no model numbers. It explicitly says current listed quarterback roles are not promised starters for the future game. Final, already-started and unverified-kickoff games do not enter this pending-context layout.

Review found a related surrounding-page defect: a started game awaiting its final result could still promise that a forecast would appear before kickoff. The shared pending notice now distinguishes future, started, final and unknown-kickoff states. A scoreboard with no forecast says no model forecast is available rather than labeling blank scores as expected points.

Three server-rendered tests verify valid fragment destinations, unavailable weather truthfulness, no model/market figures, kickoff boundary and unknown/final gates, and correct surrounding notice language. The existing 54-test application suite passed before adding the final notice regression; all three affected regressions passed afterward. Independent source review confirmed the context boundary and identified the notice issue before release.

Local browser inspection of the actual Detroit/Buffalo Week 2 page showed Jared Goff and Josh Allen as recent listed roles with timestamps and caveats, no matching weekly personnel reports, and weather outside the seven-day collection window. No current-week injury reports were relabeled as Week 2 reports. This is browser evidence for the current pending state and synthetic rendering evidence for boundary states, not physical-device acceptance.

Release `5f7cda2` received a successful [production deployment](https://vercel.com/khnum/nfl-intelligence/UuHWQ8BoZP4wZa75m7vvJnC5ZPT8). Public Detroit/Buffalo HTTP 200 confirmed the pending-context section, listed roles, no matching weekly reports and no-model label. Public completed New England/Seattle HTTP 200 confirmed the closed forecast notice and absence of pending context or a quarterback panel.

GitHub verification run 34518523459 completed successfully with the final code, including the full application/Python suites, build and dependency audit.
