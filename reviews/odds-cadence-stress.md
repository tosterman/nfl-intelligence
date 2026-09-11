# Delay and failure stress test

The 153-request candidate is feasible only under its ideal timing assumptions. `stress_odds_cadence.py` replays its exact retained request list through deterministic delay/failure scenarios. It applies the staged collector's thirty-minute reservation cooldown and 155-attempt rolling 31-day budget. Failed attempts consume both; blocked requests do not. A quote acquired at kickoff is excluded from closing coverage. These are constructed scenarios, not measured scheduler distributions or predicted failure probabilities.

| Scenario | Covered kickoff groups | Cooldown blocked | Budget blocked | Minutes without a fresh feed |
|---|---:|---:|---:|---:|
| On time, no failures | 29/29 | 0 | 0 | 0 |
| Every request five minutes late | 4/29 | 0 | 0 | 5 |
| Alternating five-minute delays | 16/29 | 3 | 0 | 5 |
| First closing request fails | 28/29 | 0 | 0 | 166.2 |
| Ten prior attempts in the rolling window | 28/29 | 0 | 4 | 1,075 |

Most candidate closing requests sit five minutes before kickoff, so a five-minute delay moves them to the excluded boundary. Uneven delay also exposes the zero-margin cooldown gaps. A failed ordinary/closing request can cause the time between successful refreshes to exceed six hours. Prior attempts matter even when the new plan fits its standalone budget.

Coverage is optimistic: successful requests assume immediately fresh bookmaker updates and immediate archive upload. The model starts without a usable prior feed, contains no retries or rescheduling, and measures freshness from acquisition only. Real source age can reduce coverage further. The prior-attempt scenario supplies budget history, not initial usable quote data. The simulation does not prove that all alternative schedules fail.

Six planning/simulation tests passed, including failures consuming budget without providing freshness, strict kickoff exclusion and exact rolling-window expiry. The full machine-readable output is `odds-cadence-stress.json`, bound to the candidate plan's hash.

Decision: do not activate the current candidate. A replacement must account for execution slack, retries and actual rolling usage, and explicitly report any kickoff groups that cannot fit. Live collection configuration, quote-age rules and the published market-pairing protocol remain unchanged.
