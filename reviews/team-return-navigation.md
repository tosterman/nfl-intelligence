# Team return navigation — September 11, 2026

The next-game and season-table links on team hubs now preserve the originating
team. The matchup breadcrumb names that destination, for example “Back to
Steelers intelligence.” Existing slate filter/search return paths are preserved.
Only the two participating teams are accepted as team return destinations;
unsupported values and repeated query parameters fall back to the game week.

Validation: three focused tests passed, TypeScript passed, and the production
build generated 319 pages. `scripts/check_team_return_ui.py` exercised both entry
points and keyboard returns for Pittsburgh and Buffalo in Chromium and WebKit
at 320 and 1280 pixels. All eight round trips passed without horizontal overflow
or page errors. Both engines also returned HTTP 200 and the slate fallback for
repeated return parameters. Results: `reviews/team-return-browser.json`.

An independent audience reviewer inspected the implementation and found no
actionable regression; that review was source-only. Browser evidence is from
the local application, not a public deployment or physical-device test.
