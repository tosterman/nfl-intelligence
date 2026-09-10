# Track-record reading guide

Added a collapsed native disclosure near the top of `/performance` explaining winner accuracy, margin/total MAE, Brier score, log loss, calibration, interval coverage, closing lines and pushes. Examples explain point error and probability scoring; the guide explicitly separates accuracy from profitable betting and notes that wider intervals are easier to hit.

An independent source reviewer checked the arithmetic and statistical interpretation and found no actionable issues. TypeScript validation passed. The local route returned HTTP 200. Chromium and WebKit at 320px and 1440px passed keyboard open/close, visible guide content, no document overflow and no page-error checks; results are in `performance-guide-browser.json`. The 320px Chromium screenshot was visually inspected after declining analytics. This is local browser evidence, not production or physical-device acceptance.

The first Python harness remained alive without results and was explicitly stopped. An instrumented file-based run completed. A subsequent screenshot exposed a harness race checking for consent before hydration; the final run waited for the banner, declined it and verified dismissal before checking the guide. No application consent behavior was changed.
