# Weekly matchup context

Goal: evolve the current static 2025 big-play and inside-20 panels into a weekly
product. Keep prior-season history and current-season samples distinct. Preserve
the existing football definitions, exact source evidence and sample denominators.
Do not change forecast numbers or imply a validated predictive effect.

## Implemented foundation

`scripts/weekly_matchup_context.py` builds the current-season component at an
exact season, phase and week. Its boundary is the earliest scheduled game date
in that scope. Only earlier weeks with completed games strictly before that
boundary are eligible. Postseason scopes include preceding regular-season games.
This is a descriptive weekly cutoff, not a claim about historical data arrival.

Retained-source loading checks the exact play and schedule hashes and applies
only hash-bound adjudications. Each eligible game must contain both offenses,
one terminal END GAME record last in source row order, and matching final scores.
That detects missing endings and score disagreements, but cannot prove that no
intermediate play was omitted. Unknown source formats fail instead of being
silently treated as complete. A week without eligible games has an explicit
`no-eligible-games` state and no invented zero rates.

Outputs retain game IDs for team sample sizes, passing/rushing numerators and
denominators, inside-20 possession/TD counts, cutoff, source hashes, adjudication
identity and observation time. They aggregate plays and possessions, not averages
of team/game percentages. Late source corrections require a new retained vintage;
older snapshot artifacts must not be silently overwritten.

## Remaining integration

1. Current-season acquisition and immutable snapshots are implemented in
   `refresh_weekly_matchup.py`. Provider asset URL, size, SHA-256 and update time
   are checked; files older than 30 hours fail. Collection completion time is
   retained separately from its start. A local real 2026 capture succeeded with
   a Week 1 `no-eligible-games` result. Prior-season rotation remains to be built;
   the existing dated 2025 panels still use their pinned archive.
2. Content-addressed weekly artifacts and manifests are retained. First public
   publication identities remain separate work; local retention proves no public
   pregame availability.
3. The shared refresh, recovery artifact paths, Git publication paths and runtime
   allowlist are wired in the development branch. The production refresh remains
   disabled pending the existing release recovery; no hosted weekly run is claimed.
4. Update both panels to show clearly separated prior/current-season samples,
   game counts, cutoffs and source observation times. Missing current data must
   leave dated historical evidence available without presenting it as current.
5. Exercise refresh failure/recovery and mobile/desktop browser behavior before
   publishing. Model integration remains a separate evaluation decision.

## Evidence

Seven targeted tests cover week boundaries, same/later-week changes, anomalously
dated later weeks, missing coverage, unfinished games, postseason transition,
partial terminal records, score disagreement and nonchronological play IDs. A
real replay caught inserted timeout IDs exceeding END GAME in KC/JAX and NE/BAL;
the check uses retained row order, not ID magnitude. Historical offline builds at
2025 Weeks 2, 10 and 18 are recorded in `reviews/weekly-matchup-replay.json`.
The pre-terminal-check and corrected post-terminal-check results share the same
artifact digests at all three boundaries (16, 135 and 256 eligible games). The
independent review is scoped to the builder, not the
unimplemented refresh or UI integration.

Acquisition has four additional tests: immutable repeat capture/corrupt existing
object rejection; bad digest/stale/future metadata rejection; and failed refresh
preserving earlier archives while replacing current state with unavailable; and
reproducing the current artifact from its retained manifest and source bytes.
An independent acquisition review found no material defect. UI integration is
still pending and must validate scope and source freshness before display.
The full Python suite passed 295 tests before the final artifact-replay test was
added; all four targeted acquisition tests then passed.
