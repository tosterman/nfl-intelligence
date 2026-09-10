# Team pages between forecast editions

The next-game card required a forecast snapshot, so New England's card disappeared after its completed first game even though its next scheduled matchup was known. Selection now depends on team membership and scheduled status, ordered by season/week/kickoff, independently of forecast availability. The card explicitly shows a pending forecast and the edition's schedule timestamp. It remains a scheduled-game view, not live score tracking.

Neutral-site matchups now use `vs.` with a visible neutral-site label in both the card and full-season table. This avoids presenting the nominal away team as traveling to its opponent's home ground.

The focused test covers unsorted input, missing forecasts and kickoff times, unrelated teams, completed/in-progress exclusions, and unchanged input ordering. TypeScript passes. Chromium and WebKit at 320px verified New England's Week 2 Steelers card, its pending forecast, and San Francisco's neutral-site Rams card and links, with no document overflow. Observations are in `team-next-game-browser.json`.

The independent founding-scope review's next larger recommendation is a weekly change briefing on the slate: surface retained compatible revisions, new forecasts and model-version changes without inventing football causes. It can reuse the current revision/comparison functions and must distinguish generated revisions from verified publication. That briefing is not implemented by this team-page correction.
