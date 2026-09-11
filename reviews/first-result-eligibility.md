# First result eligibility — September 11, 2026

At 16:16:24 UTC, a read-only fetch of the configured nflverse schedule returned
final scores for New England–Seattle and San Francisco–Los Angeles. Source:
https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv
SHA-256: `664dd4abffd99b29efc5cf875a800c25631c190cb4e4522fb5354e61781369bf`.

Neither game currently qualifies for the strict prospective record. For SF–LA,
seven earlier snapshots have valid hashes and pregame publication receipts but
lack the required immutable game context. The September 10 23:29:01 UTC snapshot
has matching context and a valid hash, but no public publication receipt.
Running the existing eligibility and grading functions against copied game
objects with the fetched results therefore yields zero eligible games and two
missed games. No production artifact, score or forecast was modified.

Do not backfill context into old snapshots or count the unpublished local
snapshot. A successful fresh public edition before upcoming kickoffs is needed
to start the strict prospective record. A historical public receipt by itself
does not establish eligibility under the current context requirements.

This is a diagnostic availability check, not an archived fresh edition or an
independent score adjudication. The next full refresh must acquire, validate and
retain its own actual source bytes, then verify publication archives and replay.
