# Live calibration

The prospective grader now computes descriptive calibration from its existing receipt-qualified decisive records. It cannot borrow historical development rows or tied results. Fixed bands match the established retrospective display: [0,.4), [.4,.5), [.5,.6), [.6,.7), [.7,1]. These were fixed before any eligible live results arrived; no probability mapping or model parameter was changed.

Each occupied band reports the average original forecast, observed home-win fraction, count and 95% Wilson interval (z=1.96). Boundary probabilities enter the upper band except 1, which remains in the final band. Empty bins are omitted rather than plotted as zero accuracy. Invalid nonfinite/out-of-range probabilities and nonbinary outcomes fail validation. The UI explains the conditional-on-decisive-game interpretation, small-sample uncertainty and independence assumption behind Wilson intervals.

Three calculation tests cover every boundary, single-win/single-loss intervals, empty samples and invalid data. Publication integration checks verify only the selected eligible original probability contributes, while ties and missing receipts contribute no bins. A server-rendered UI test distinguishes empty evidence from one observed loss, including its wide interval and keyboard-scrollable semantic table. Independent review found no material defect. All 51 application tests, six publication tests, three calibration tests and the production build pass.

The actual live sample is still empty. This implements the prospective calibration calculation and display; it does not demonstrate calibration, future accuracy or profit. Populated states are synthetic test evidence, not actual game results. The site aggregate was recomputed from the existing game/ledger/receipt artifacts without regenerating forecasts or changing source timestamps.

Local browser review verified the empty calibration state, its position within the live record and its accessible heading. Review also prompted a clearer separation: the historical-replay warning now sits directly above the historical metrics under a dedicated heading, instead of appearing above both records. The two server-rendering regressions pass after this layout correction.

Release `ba5bdb4` received a successful [production deployment](https://vercel.com/khnum/nfl-intelligence/7HYYFYJ32pdmpHbvyfXLXRvhHjZi). Anonymous HTTP verification returned 200 and checked the ordering of live record, live calibration, historical heading and retrospective warning. The live calibration empty-state text was present.

GitHub verification run 34516713071 completed successfully for this release, including Python tests, application tests, production build and dependency audit.
