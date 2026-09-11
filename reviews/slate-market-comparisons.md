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

Visual mobile review and comparison-density refinement remain pending. The clock
fixture proves behavior, not the appearance of styled slate cards. No public
deployment was performed.
