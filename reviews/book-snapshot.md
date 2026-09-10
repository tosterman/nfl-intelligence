# Sportsbook snapshot comparison

Matchup market panels now include an expandable side-by-side table of all currently eligible books. It preserves each market's observation time, both sides' prices, home/away spread direction, and over/under prices. Home-spread and total ranges report the minimum and maximum quoted points and the count of books supplying that market. They do not claim simultaneous consensus, executable best price, validated edge, or expected return.

The component receives only `assessGameOdds` output. Existing event identity, quote timing, six-hour expiry and kickoff closure continue to control inclusion and update with the page clock. Missing or filtered markets read “No eligible quote.” The existing selected-book comparison remains available.

The fixture regression includes two eligible books with different spread observations and an expired third book. It verifies the range and excludes the expired book. All 93 application tests passed before the final label clarification; the three affected market-display tests were rerun afterward. TypeScript checking passed. Independent automated UX review found no blocking issue and requested the more precise missing-quote label, which was adopted.

The local real-feed SF/LA page displayed nine eligible books in Chromium and WebKit at 320 and 1440 pixels. Keyboard expansion and horizontal scrolling passed, with no document overflow. Mobile table content retains 680 pixels of width inside its scrollable region to avoid compressing prices and timestamps into unreadable columns. The mobile view was visually inspected and the scroll hint moved above the table. Evidence is retained in `book-snapshot-browser.json`.

This used retained odds and did not request a new paid provider collection. The data and model were not modified. Production deployment, real-device and human assistive-technology acceptance remain outstanding.
