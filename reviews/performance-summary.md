# Data-bound performance conclusion

The track-record page had a fixed sentence asserting that the model improved on winner baselines and that the closing market estimated margins more accurately. Although consistent with the current edition, it could survive a later reversal or missing comparison data.

The margin conclusion now uses the same matched-model and market margin-error fields as the comparison table, names the matched sample size, and compares at the table's displayed precision. Missing, nonfinite, negative or empty evidence yields an unavailable message. It describes retrospective sample error and does not establish a reliable betting advantage. The unsupported fixed winner-baseline narrative was removed; the actual baseline table remains.

Two focused tests cover reversed rankings, equality at displayed precision, invalid/missing errors and invalid sample counts. TypeScript checks pass. Chromium checks at 320px and 1440px verified the current 570-game conclusion and no document overflow; `performance-summary-browser.json` retains the observed text. No forecasts or evaluation data changed.
