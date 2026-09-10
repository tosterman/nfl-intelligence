# Public uncertainty diagnostics

The local performance page now computes outcome interval coverage from the current historical records on the server. It displays all games and the existing four fixed absolute model-versus-closing-margin bands, with covered counts, denominators, percentages and average range widths for margin and total separately. No historical interval arrays are added to client component props. Missing-market games remain in the overall row and are explicitly excluded from bands.

The current edition reconciles with the independent Python analysis: 463/570 margin outcomes covered overall, 470/570 totals, and 22/35 margins in the 6+ disagreement group. Copy identifies development evidence, small samples, separate marginal coverage, and the lack of a validated betting opportunity. The production model is unchanged.

Verification: two new tests first failed due to the absent helper, then passed. They cover inclusive endpoints, width, missing-market grouping, malformed intervals, duplicate identities and current-edition reconciliation. All 116 application tests passed, type checking passed, and the production build completed. Chromium and WebKit at 320px and 1440px showed five rows, expected counts, no page errors or document overflow, and keyboard access to the final column. A first visual pass prompted a 680px minimum table width to avoid compressed number columns; the mobile table scrolls within its labeled focusable region. The keyboard check was rerun with realistic key timing to allow animated scrolling to complete. See interval-coverage-browser.json.

These checks do not establish full accessibility compliance, new prospective accuracy or a public deployment. This is a local product addition awaiting release.
