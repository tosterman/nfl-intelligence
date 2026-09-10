# Consolidated production-build verification

Source commit `edef55a4fe19c15b88b42048c90209e64ce81aea` was exported through Git archive into an isolated directory, built with Next.js production webpack output, and served on localhost port 3001. No production artifact, development server build directory, or provider credential was changed. The build completed all 319 generated pages and TypeScript validation.

Eighteen route visits covered the slate, ratings, performance, SF/LA matchup, Philadelphia team page and privacy page: Chromium at 320 and 1440 pixels, and WebKit at 390 pixels. Every response was HTTP 200, with one H1, no page errors and no document-width overflow. Decline persisted through navigation, and the matchup's historical-participation section opened with keyboard input. Results and build ID are retained in `current-production-browser.json`.

The same source commit passed [hosted verification 34535368028](https://github.com/tosterman/nfl-intelligence/actions/runs/34535368028), including application/Python tests, production build and production dependency audit.

This supersedes the older isolated browser build for the tested routes. It does not verify provider-backed market rendering in production: the isolated server intentionally had no provider credentials. Separate local real-feed and fixture evidence covers sportsbook comparisons and contribution revisions. It also does not establish real-device, human assistive-technology, sustained scheduler, live rollout, publisher, or revenue acceptance. The temporary production server was stopped after verification.
