# Slate market comparisons — implementation checkpoint

Market cards now show the default selected sportsbook's spread, total, prices
and separate observation times. With fresh model inputs, they also show the
home team's point difference from the spread and the total's higher/lower
difference. Differences are explicitly not proven betting edges. Missing,
expired and closed markets retain the existing availability rules.

The card receives the same model-source freshness inputs used on the slate.
Its timer now includes model deadlines as well as each market's deadlines.
Layout moves the market section below the two model values rather than squeezing
the additional text into the previous third column.

Five market-display/deadline tests passed, covering both spread directions,
total direction, equality, stale model, stale quotes and kickoff. TypeScript
checking passed. Chromium and WebKit clock tests passed, including removal of
the new total difference when model inputs expire. No page errors were reported.

Styled visual review now covers Chromium and WebKit at 320, 390 and 1280px.
The actual local slate had no horizontal overflow at those sizes. An isolated
populated synthetic quote fixture uses the real Slate component and actual app
styles; all six cases showed both differences and the selected book, with no
horizontal overflow or automated WCAG A/AA violations. The 390px card screenshot
was visually inspected. Model values remain above the separate market section;
each quote has its own observation time. The synthetic scores reconcile to the
specified margin and total before display rounding.

TypeScript checking passed with the fixture. This is bounded browser/automated
accessibility evidence, not timed human scanning or complete accessibility
certification. No public deployment was performed.
