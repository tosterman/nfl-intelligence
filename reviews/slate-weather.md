# Slate weather review

Upcoming matchup cards now show a compact kickoff-hour outdoor forecast using
the same retained weather evidence and schedule/freshness selector as game pages.
Only summary text and its expiry cross the server/client boundary; page views do
not acquire new provider data. No weather adjustment was added to the model.

Temperature, wind and precipitation retain zero values. Missing, stale and
rescheduled evidence displays its availability reason. Outdoor conditions are
explicitly separated from unknown roof/field conditions. The client removes
values at the first expired millisecond and hides the forecast at kickoff.
The existing card link leads to the detailed source and limitations.

Seven selector tests passed, including the inclusive 30-hour boundary and invalid
measurement rejection. TypeScript checking and production build passed. Real
local-page checks cover Chromium/WebKit at 320, 390 and 1280px: no horizontal
overflow, page errors or automated WCAG A/AA violations in the game grid.
Isolated actual-component clock checks verify expiry and kickoff in both engines.

Independent UX review identified missing horizontal inset; corrected to 20px,
matching the card footer, then reran the browser checks. Automated checks do not
prove timed human comprehension or comprehensive accessibility. Public deployment
and full launch acceptance remain outstanding.
