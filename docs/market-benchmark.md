# Matched forecast and market errors

This implementation extends the unchanged market-pairing v1 observations into descriptive score-error accounting. It is not yet wired to the public performance page or scheduled publisher. It is not a separately verified preregistration receipt and does not calculate betting settlement, return or CLV.

For each book, spread and total remain separate. Use the latest valid forecast published by the protocol's 24-hour entry checkpoint and a sampled market observation from the final 15 minutes before kickoff. A spread of home -3 corresponds to a market-implied home margin of +3. Compare absolute model and market errors against the same retained final result. Include tied scores. Each mean uses exactly the same games for that book/market; empty cohorts have null means, never zero error. No favorable-book selection or older-quote fallback is permitted.

Final scores must match the exact retained schedule bytes and game context, with source acquisition after kickoff and no future acquisition/edition timestamps. Every private paired record identifies its snapshot, publication receipt, quote capture/update/upload and result source. Pending results remain separate from missing or stale checkpoints. Exclusion reasons can overlap and must not be summed as unique games.

Run `python scripts/report_market_benchmark.py --export <verified-local-export>` using an authenticated retained odds export. It makes no provider requests, verifies the original pairing protocol, retains report inputs/code/captures privately, and writes the sanitized aggregate to `reviews/market-benchmark-summary.json`. Replay the resulting report with `python scripts/replay_market_benchmark.py <reportHash>`; the checker verifies dependencies and runs the pinned grader with networking blocked.

The September 11 real run used archive coverage through 00:38 UTC, not a new export. It produced zero paired games: one pre-protocol closing checkpoint, one evaluated closing checkpoint and 270 future checkpoints. The evaluated game's nine books each lack an eligible closing capture and its entry checkpoint predates activation. This is 18 excluded book/market rows, not 18 games. No capture window was widened.

Validation: 31 market-related Python tests passed, including nine new benchmark tests. Independent code review found and prompted the future-edition rejection. The retained real report replayed exactly with zero paired games and networking blocked; see `reviews/market-benchmark-replay.json`.

Before public acceptance: verify a published scoring convention, wire and validate the sanitized performance view, retain production reports durably, integrate refresh/replay into the operational workflow, and observe actual qualified captures and results. A private report or fixture pass is not a public benchmark or proof of accuracy.
