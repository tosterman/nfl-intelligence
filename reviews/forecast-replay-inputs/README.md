# Fixed numerical replay edition

This bundle retains the real edition generated September 10, 2026 at 23:29:01.710181 UTC, its schedule, and 2010–2026 weekly team-stat input files. It is a test fixture, never an input to production refresh or a current-data fallback. The manifest binds compressed and restored bytes and expects all 15 current forecasts to reproduce exactly.

Run `python scripts/replay_retained_fixture.py` from the checkout. It restores files into a temporary directory, blocks HTTP/socket connections during inference, checks that restored files remain unchanged, and requires complete numerical agreement. It uses the running engine whose recorded code hash must match the edition. Engine changes require a deliberately reviewed replacement fixture or preservation of the compatible engine; do not weaken comparisons to make the check pass.

The schedule and team statistics are attributed to [nflverse](https://github.com/nflverse/nflverse-data) under [CC BY 4.0](https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md). Original URLs, source hashes and acquisition times are retained in the compressed site artifact. The derived site artifact contains NFL Intelligence forecasts. Current historical inputs can contain retrospective corrections: replayability is not historical vintage availability, independent forecast skill or proof of pregame publication.
