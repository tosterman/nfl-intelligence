# Confidence and market-disagreement diagnostics

Founding section 30 requires performance by confidence and disagreement size. The performance page now groups retained retrospective development records into fixed confidence bands (50–<60%, 60–<70%, 70–<80%, 80–100%) and absolute home-margin disagreement bands (0–<2, 2–<4, 4–<6, 6+ points). Boundaries were declared for description, not optimized against results.

Each band exposes constituent games, winner counts, tied games, margin/total errors and unthresholded closing-spread settlements. Missing markets, pushes and zero-direction cases remain distinct. The UI explicitly separates these diagnostics from the existing thresholded ATS selections and from receipt-qualified prospective results. No prices, stakes, vig, returns or profitable-edge claims are inferred.

Tests cover boundaries, ties, loss direction, pushes, missing markets, invalid/duplicate rows and empty groups. Real-data totals reconcile to the existing 570-game record, including 569 decisive results, one tie and 361 correct winners. Independent code review found no material arithmetic or labeling issue. TypeScript checking and mobile Chromium/WebKit keyboard disclosure checks passed. The games table uses bounded scrolling; `performance-bands-browser.json` records the browser checks.

These are development-branch changes. They strengthen auditability, not predictive accuracy, and are not yet verified on the public deployment.
