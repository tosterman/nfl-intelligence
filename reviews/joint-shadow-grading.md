# Archived joint-score grading

`python scripts/grade_joint_shadow.py` validates the archive/manifest/publication receipt chain, frozen protocol, prior and fit metadata, and point-snapshot hashes. It also checks the current scoring implementation against the frozen scorer fingerprint, so changing a score formula cannot silently rewrite this research track. The output records the result-source and grading-code fingerprints.

The first verified publication per game wins, regardless of later revisions. Current home/away, season/week/type and kickoff must agree; equivalent timezone representations of the same kickoff are accepted. Missing results remain pending, while changed identities are explicitly excluded pending reconciliation. Invalid final scores, mismatched grids, invalid distributions or zero probability for an observed outcome fail instead of dropping the game or clipping its score. The grader reads full archived matrices; it does not call the solver or rebuild distributions.

Scores include joint/margin/total log score, discrete margin/total CRPS and three-outcome Brier. The paired joint-log-score comparison uses whole-week resampling, withholding the interval when a season has fewer than two week clusters. No completed games yields a null summary, not zero error. Current result: **0 graded, 15 pending, 0 excluded**.

Five tests cover first-capture selection, missing results, changed/offset-equivalent kickoffs, late receipts, invalid results, validation of the actual archived publication, and rejection of changed scoring code. Independent review reproduced the current pending counts and identified the scorer-enforcement gap, which was fixed with a regression test. This validates stored publication evidence; it does not perform a fresh GitHub retrieval on every grading run or claim protection against someone rewriting all trusted local code and evidence together.

The grader is an offline research command at this checkpoint. Scheduled research grading and prospective final-result evidence remain unfinished. Production forecasts and the public model record are separate.
