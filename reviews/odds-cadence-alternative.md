# Earlier acquisitions with bounded timing slack

The second offline candidate retains the 155-attempt cap and fixed fifteen-minute closing window. It targets acquisitions ten minutes before kickoff, spaces planned requests at least twenty minutes apart, and simulates a fifteen-minute acquisition cooldown. That is a proposed change to the staged collector's thirty-minute cooldown, not a change to the bookmaker quote-age policy. No collector or workflow configuration was modified.

Using the same fixed 31-day input as the first experiment, the candidate still uses 153 requests. It covers all 29 kickoff groups when requests are on time, all five minutes late, or alternately five minutes late in either parity. None of those scenarios hits the proposed cooldown. This improves on the earlier candidate's 4/29 coverage when every request is five minutes late. Successful requests still assume fresh bookmaker updates and immediate storage upload.

The candidate does not solve failure recovery or budget history. A failed first closing request leaves 28/29 groups covered and approximately 165.8 minutes without a fresh feed. Ten prior attempts cause four budget rejections and 1,075 minutes without fresh data in the constructed scenario. Two spare attempts are insufficient evidence of operational resilience.

`compare_odds_cadences.py` rejects a changed schedule hash, retains the full new request list and runs both candidates' shared simulation rules with the explicitly different cooldown. `odds-cadence-alternative.json` records the outputs. Seven planning/simulation tests passed, including a close pair of kickoff groups under both alternating delay patterns. No claim of optimality, real scheduler delay distribution or guaranteed provider freshness is made.

Next: incorporate actual rolling usage and bounded recovery without spending requests on obsolete checkpoints. Live activation still requires an executable schedule, verified scheduler behavior and a reviewed collector configuration; this experiment alone is not sufficient.
