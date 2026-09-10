# Conditional uncertainty audit

This audit uses the existing 570 retrospective development records and the same fixed confidence/disagreement bands as the performance page. It does not refit the model, select thresholds, test significance or create prospective evidence. The JSON binds the analysis to exact edition bytes and retains the identities of every interval miss.

Overall margin coverage is 463/570 (81.23%); total coverage is 470/570 (82.46%). Both ranges target 80%. Coverage alone can reward excessively wide intervals, so the report also includes mean width and central-80% interval score: width plus ten times the distance of an outcome outside the interval. Lower interval score is better.

| Absolute model–closing-market margin difference | Games | Margin covered | Total covered |
|---|---:|---:|---:|
| 0–<2 points | 305 | 83.28% | 84.59% |
| 2–<4 points | 163 | 82.82% | 79.75% |
| 4–<6 points | 67 | 77.61% | 82.09% |
| 6+ points | 35 | 62.86% | 77.14% |

The largest-disagreement band contains 22 covered margins and 13 misses. This is a descriptive warning against interpreting greater disagreement as greater model reliability. It does not establish statistical significance, a causal explanation, a profitable strategy or stable future undercoverage. Games can be dependent and the sample has already been inspected during development. No model parameter or interval width was changed in response.

Confidence-band margin coverage is 82.92%, 80.34%, 77.42% and 83.33%, respectively; the highest band contains only 18 games. Further interval modeling must be evaluated through a separately specified experiment and new prospective evidence, rather than tuning these bands to make the current record look better.

The unit checks cover inclusive endpoints, tail direction, width/miss penalty, missing-market exclusion, band boundaries, malformed intervals and duplicate identities. Run `python scripts/interval_diagnostics.py` to reproduce against the current checked-in edition; a different edition will produce a different source digest.
