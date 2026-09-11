# Inside-20 matchup presentation

Forecast-bearing matchup pages now compare both offenses with the opposing
defenses using historical inside-20 offensive touchdown rates. Each percentage
shows its touchdown count and possession denominator. The page labels 2025
regular season and playoffs, the strictly-inside-20 boundary, and the absence of
opponent or roster adjustment. These descriptive rates do not alter forecasts.

Definitions explain penalties, repeat entries, long touchdowns, defensive
returns and conversion sequences. The section navigation links to its heading.
Incompatible seasons, unknown teams and missing/invalid kickoff dates show an
unavailable state. The component renders on the server. The deployment allowlist
includes its runtime JSON artifact; retained raw sources remain excluded.

Verification: 129 application tests and the production build passed. The release
file coverage test passed. The browser audit checked 15 matchups in Chromium and
WebKit at 320px: all 120 red-zone rates and 240 big-play rates matched retained
counts, with no page errors or document overflow. Chromium additionally checked
the section anchor and expandable definition; its mobile capture was inspected.

The audit initially exposed Python's tie-to-even formatting versus the UI's
half-up display (27/48 = 56.25%). Decimal half-up expectations now handle that
case explicitly. No source count was changed to satisfy a rendering check.

Independent expert review and public deployment remain outstanding. These
checks verify the described local component, not the complete launch objective.
