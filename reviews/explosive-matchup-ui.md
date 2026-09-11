# Big-play history on matchup pages

Current forecast-bearing matchup pages now show two comparisons: the away
offense against the home defense, and the home offense against the away defense.
Passing and rushing rates display both numerator and denominator. The section
labels the 2025 regular season and playoffs, equal eligible-play weighting, lack of
opponent/roster adjustment, and separation from the forecast. Definitions and
nflverse attribution are available in an expandable source panel.

The server component withholds incompatible teams, seasons, missing kickoffs and
dates before the artifact cutoff. It sends rendered summary values rather than
the complete per-game data to client components. A game navigation link leads
directly to the section. Pages without a forecast currently retain their existing
pending-context layout; broader placement remains a follow-up.

Verification: 126 application tests passed; production build passed. Chromium
and WebKit at 320px rendered both comparison tables and eight rate values with
no page errors or document overflow. The definitions control opened in both
engines. Chromium also verified the navigation anchor after declining analytics.
The mobile screenshot was visually inspected for legibility. These checks are
not an independent expert review or a claim of predictive validation.
