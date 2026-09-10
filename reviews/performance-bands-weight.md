# On-demand diagnostic rows

The performance page previously rendered every constituent row twice, even while all eight disclosures were closed. It now server-renders the summaries and renders each table only when that native disclosure opens. Closing removes those rows. Only the nine required record fields are passed to the client component; no additional data request is needed to inspect a band.

Matched local production-build observations: initial DOM elements fell from 14,210 to 370; decoded HTML from 978,736 to 155,894 bytes; compressed HTML from 106,685 to 26,326 bytes. Before/after observations are in `local-page-weight-before.json` and `local-page-weight.json`. These are single local measurements of document size, not total network weight, representative Core Web Vitals or proof of real-user latency improvement. The client interaction adds JavaScript work; game rows require JavaScript to open.

The production build and four diagnostic arithmetic tests passed. Chromium and WebKit at 320px still opened and closed the first 281-row band by keyboard, preserved all rows and avoided document overflow. Reader checks also reached the last of eleven columns. The temporary production server on port 3001 was stopped; normal development remains on port 3000. No deployment occurred.
